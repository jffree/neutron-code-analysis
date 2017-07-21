# OVS DB IDL

## `class SchemaHelper(object)`

对 ovsdb database schema 的封装，便于创建 IDL。

### `def __init__(self, location=None, schema_json=None)`

```
    def __init__(self, location=None, schema_json=None):
        if location and schema_json:
            raise ValueError("both location and schema_json can't be "
                             "specified. it's ambiguous.")
        if schema_json is None:
            if location is None:
                location = "%s/vswitch.ovsschema" % ovs.dirs.PKGDATADIR
            schema_json = ovs.json.from_file(location)

        self.schema_json = schema_json
        self._tables = {}
        self._readonly = {}
        self._all = False
```

1. ovsdb 的 database schema 的获取有两种方法：一个是通过 JSON-RPC 从 ovsdb 中读取（也就是 schema_json），另外一个是从 schema 文件中读取（location 代表了文件的位置）。
2. `schema_json` json 格式的 schema 数据
3. `_tables`：表示对 schema 感兴趣的需要跟踪的 table
4. `_readonly`：有哪些表是只读的
5. `_all`：若该属性为 True，则表示对 schema 中所有的 table 感兴趣

### `def register_all(self)`

```
    def register_all(self):
        """Registers interest in every column of every table."""
        self._all = True
```

### `def get_idl_schema(self)`

1. 从 schema 数据中构造 `DbSchema` 实例。
2. 选择 schema 中感兴趣的表进行跟踪。（`self._all` 为 True 的话表示对 schema 中所有的表感兴趣）

## `class Idl(object)`

将 ovsdb 中的数据库拿到内存中来处理。

```
        assert isinstance(schema, SchemaHelper)
        schema = schema.get_idl_schema()

        self.tables = schema.tables
        self.readonly = schema.readonly
        self._db = schema
        self._session = ovs.jsonrpc.Session.open(remote)
        self._monitor_request_id = None
        self._last_seqno = None
        self.change_seqno = 0

        # Database locking.
        self.lock_name = None          # Name of lock we need, None if none.
        self.has_lock = False          # Has db server said we have the lock?
        self.is_lock_contended = False  # Has db server said we can't get lock?
        self._lock_request_id = None   # JSON-RPC ID of in-flight lock request.

        # Transaction support.
        self.txn = None
        self._outstanding_txns = {}

        for table in schema.tables.itervalues():
            for column in table.columns.itervalues():
                if not hasattr(column, 'alert'):
                    column.alert = True
            table.need_table = False
            table.rows = {}
            table.idl = self
```

初始化一系列的属性，同时为感兴趣的表建立存储。

* `tables`：该 IDL 维护（感兴趣的）的数据库表格。
* `change_seqno` 表示该 IDL 更新记录。该值在两种状态下会发生改变：第一种是 IDL 更新时（运行 idl.run 方法）；第二种是与 server 的连接丢失并且重新进行连接时会更改，这个更改将会让 IDL 重新加载 server 数据库。
* `lock_name` 该 IDL 占有的锁的名称（可能会有多个客户端访问 ovsdb，此时需要锁机制）
* `has_lock` 该 IDL 是否拥有锁
* `is_lock_contended`：锁是否被别的客户端占有
* `_lock_request_id`：
* `txn`：`ovs.db.idl.Transaction` 的对象，负责与数据库进行交易。
* `_outstanding_txns`：
* `_monitor_request_id`：发送的 `monitor` 消息的 id（用来监测接收到的消息是否为 monitor 回复的消息）
* `_last_seqno`：与 session.seqno 相同。当与 session.seqno 不同时，说明与 ovsdb server 的链接出现了不同步（断开并再次重新连接）。
* `uuid`
* `state`：该 IDL 的状态

### `def force_reconnect(self)`

重置 session 连接

### `def __clear(self)`

清空当前 IDL 中的所有记录

### `def __send_monitor_request(self)`

调用 ovsdb server 的 `monitor` 方法，监听所有感兴趣表（`self.tales`）中的非只读 column。

* 相当于调用如下方法：
 1. `ovsdb-client monitor ALL` 监听所有表的变动
 2. `ovsdb-client monitor 'tcp:127.0.0.1:6640' 'Open_vSwitch' 'Bridge' netflow protocols` 监听指定表中 column 的变动（`send request, method="monitor", params=["Open_vSwitch",null,{"Bridge":[{"columns":["netflow"]},{"columns":["protocols"]}]}], id=2`）

并将发送消息的 id 设置为 `_monitor_request_id`

### `def __send_lock_request(self)`

```
    def __send_lock_request(self):
        self._lock_request_id = self.__do_send_lock_request("lock")
```

相当于执行 `ovsdb-client -v lock 'sdas'` 命令（具体消息呈现为：`send request, method="lock", params=["sdas"], id=0`）。

### `def __send_unlock_request(self)`

```
    def __send_unlock_request(self):
        self.__do_send_lock_request("unlock")
```

### `def __do_send_lock_request(self, method)`

向 ovsdb server 发送占有锁或者释放锁的命令。

### `def __parse_lock_reply(self, result)`

当发送占有 lock 的命令时（`__send_lock_request`）会收到 ovsdb server 收到的回复（`received reply, result={"locked":true}, id=0`）。

该方法负责解析收到的回复，并调用 `__update_has_lock` 方法设置该 IDL 是否占有锁。

### `def __parse_lock_notify(self, params, new_has_lock)`

当一个 client 占有锁的情况下，另一个 client 用相同的命令来请求锁。第二个请求锁的 client 会收到请求失败的 replay，而已经占有锁的 client 会收到一个 notify（`received notification, method="locked", params=["sdas"]`）。

该方法就是解析 notify 的返回包。


### `def set_lock(self, lock_name)`

调用 `__send_lock_request` 尝试去占有锁

### `def __parse_update(self, update)`

调用 `__do_parse_update` 实现。

我们用下面这个命令来做测试：

* `ovsdb-client -v monitor 'tcp:127.0.0.1:6640' 'Open_vSwitch' 'Bridge' netflow protocols`
* 收到的 reply 为（json 格式的，可以找个 json 解析器来看）：`{"Bridge":{"407f3645-862e-4ac0-98ae-7a46cfdaa4ec":{"new":{"netflow":["set",[]],"protocols":["set",["OpenFlow10","OpenFlow13"]]}},"d40ac0ea-e7d9-4ab1-83c5-168bdc45c6ba":{"new":{"netflow":["set",[]],"protocols":["set",["OpenFlow10","OpenFlow13"]]}},"f779e141-0ac0-4b38-8b61-50e199ea1da8":{"new":{"netflow":["set",[]],"protocols":["set",["OpenFlow10","OpenFlow13"]]}}}}`

### `def __do_parse_update(self, table_updates)`

1. 检查收到的数据格式是否正确。
2. 调用 `Parser` 进行数据解析。
3. 调用 `__process_update` 处理数据

数据说明：
 1. 每个表都有一个 name
 2. 每个表的记录都有一个 uuid 数据作为该表项的 id
 3. 每个记录可能有 old 和 new 的记录，old 指改变前的数据，new 指改变后的数据

### `def __process_update(self, table, uuid, old, new)`

* 参数说明
 1. table 待更新的表名
 2. uuid 表下面记录的 id
 3. old 该记录的旧数据
 4. new 该记录的新数据 

根据数据的内容，来删除记录、更新记录、创建记录。

### `def run(self)`

更新 IDL，处理一系列从 ovsdb server 接收到的消息。

1. 根据 `_last_seqno` 与 session.seqno 的差异判断是否与 ovsdb server 进行了重新连接。
 * 若有重新连接发生，则需要重新调用 `__send_monitor_request` 和 `__send_lock_request` 重新开始监听 
2. 调用 `_session.recv` 接受消息，并根据消息的种类去处理消息。
 1. 消息的类型为 `notification`，方法为 `update`，则是数据库有更新
 2. 消息的类型为 `reply`，且消息的 id 与 `_monitor_request_id` 相同，则此消息为开始监听时收到的回复消息（该消息包含了被监听表中 column 的当前值）。
 3. 消息的类型为 `reply`，且消息的 id 与 `_lock_request_id` 相同，则此消息为请求锁命令的回复消息。
 4. 消息的类型为 `notification`，方法为 `locked`，则此消息意味着有别的 client 请求相同的锁
 5. 消息的类型为 `notification`，方法为 `stolen`，则此消息意味着有别的 client 偷走了我们当前所拥有的锁
 6. 对于 `echo` 的消息忽略处理 

### `def __create_row(self, table, uuid)`

创建一个 `Raw` 对象，来表示数据库的某一表的某个记录

### `def __row_update(self, table, row, row_json)`

用 `Datum` 的实例来更新 Raw 记录