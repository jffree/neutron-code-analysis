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

## `class Transaction(object)`

## 测试

* 执行命令：`ovs-vsctl -v add-br test`
* 提取输出中的关于 **transact** 的消息如下：

```
2017-07-21T16:33:33Z|00013|jsonrpc|DBG|unix:/var/run/openvswitch/db.sock: send request, method="transact", params=["Open_vSwitch",{"rows":[{"interfaces":["uuid","a5824cf3-9725-4bf4-85fe-9a08cb9991bd"]}],"until":"==","where":[["_uuid","==",["uuid","02882f40-abdd-4839-8169-2c21ebccf0ba"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"ports":["set",[["uuid","5a648cbb-9db2-467a-af70-0ae1ab963f24"],["uuid","ba649eb8-4b73-4b23-a098-1248af76b17c"]]]}],"until":"==","where":[["_uuid","==",["uuid","f779e141-0ac0-4b38-8b61-50e199ea1da8"]]],"columns":["ports"],"timeout":0,"op":"wait","table":"Bridge"},{"rows":[{"bridges":["set",[["uuid","407f3645-862e-4ac0-98ae-7a46cfdaa4ec"],["uuid","d40ac0ea-e7d9-4ab1-83c5-168bdc45c6ba"],["uuid","f779e141-0ac0-4b38-8b61-50e199ea1da8"]]]}],"until":"==","where":[["_uuid","==",["uuid","d3d393e2-d5b9-4b7e-bb91-071a53ccc6ab"]]],"columns":["bridges"],"timeout":0,"op":"wait","table":"Open_vSwitch"},{"rows":[{"interfaces":["uuid","32ec4baf-e96a-4fd9-bebf-be51b14513d7"]}],"until":"==","where":[["_uuid","==",["uuid","cc656684-a310-49df-a7a1-aa12106560db"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","38f6ba3a-efb7-45a1-80d9-d3a13b496247"]}],"until":"==","where":[["_uuid","==",["uuid","4da79a34-40d7-4719-be95-81d1b3f4bc64"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"ports":["set",[["uuid","f1d2699f-da02-4b03-a291-b9c053c8ac36"],["uuid","f7044107-8cf9-4b79-855d-adde64a69a64"]]]}],"until":"==","where":[["_uuid","==",["uuid","407f3645-862e-4ac0-98ae-7a46cfdaa4ec"]]],"columns":["ports"],"timeout":0,"op":"wait","table":"Bridge"},{"rows":[{"interfaces":["uuid","4dc8987f-da12-4e40-ab63-f044cfe55468"]}],"until":"==","where":[["_uuid","==",["uuid","aee9c6b6-24c9-4a4d-9f93-bc6e48c87528"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","7e38e71e-acea-456c-a45b-133fe418c2c1"]}],"until":"==","where":[["_uuid","==",["uuid","f7044107-8cf9-4b79-855d-adde64a69a64"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","c1a14b55-ff31-432d-a0ce-b2223489a273"]}],"until":"==","where":[["_uuid","==",["uuid","6deb3707-6768-4766-a540-dfd8c78bb8ac"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","608e31db-07dc-47ed-80a7-cb2f4d6bed63"]}],"until":"==","where":[["_uuid","==",["uuid","ba649eb8-4b73-4b23-a098-1248af76b17c"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","806361e3-cf54-49c5-8601-759ca8513b24"]}],"until":"==","where":[["_uuid","==",["uuid","8ae3d5ba-d33b-4dd1-ac9b-9a4e0b1848ab"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","3a351c15-31d2-497d-abe9-ae06b5ad542d"]}],"until":"==","where":[["_uuid","==",["uuid","32dc6e6a-8259-495a-b9fe-da10678984e0"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"ports":["set",[["uuid","02882f40-abdd-4839-8169-2c21ebccf0ba"],["uuid","32dc6e6a-8259-495a-b9fe-da10678984e0"],["uuid","4da79a34-40d7-4719-be95-81d1b3f4bc64"],["uuid","6deb3707-6768-4766-a540-dfd8c78bb8ac"],["uuid","8ae3d5ba-d33b-4dd1-ac9b-9a4e0b1848ab"],["uuid","967fd5ed-17c4-4149-ac4c-81b77cb3b8ba"],["uuid","a90c5a2b-688b-46cd-9902-a6c93c66a514"],["uuid","aee9c6b6-24c9-4a4d-9f93-bc6e48c87528"],["uuid","cc656684-a310-49df-a7a1-aa12106560db"]]]}],"until":"==","where":[["_uuid","==",["uuid","d40ac0ea-e7d9-4ab1-83c5-168bdc45c6ba"]]],"columns":["ports"],"timeout":0,"op":"wait","table":"Bridge"},{"rows":[{"interfaces":["uuid","d2df8751-ab37-4689-9510-b7a2b12ac58a"]}],"until":"==","where":[["_uuid","==",["uuid","5a648cbb-9db2-467a-af70-0ae1ab963f24"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","808a3b33-cd49-4239-9e9c-4c12f021cc01"]}],"until":"==","where":[["_uuid","==",["uuid","a90c5a2b-688b-46cd-9902-a6c93c66a514"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","37ebda85-861b-469f-9d20-2d3d89c20c73"]}],"until":"==","where":[["_uuid","==",["uuid","967fd5ed-17c4-4149-ac4c-81b77cb3b8ba"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"rows":[{"interfaces":["uuid","e3be6f03-c335-4477-9b9e-8406bdce124e"]}],"until":"==","where":[["_uuid","==",["uuid","f1d2699f-da02-4b03-a291-b9c053c8ac36"]]],"columns":["interfaces"],"timeout":0,"op":"wait","table":"Port"},{"uuid-name":"rowaf607491_b948_40a9_8fa3_52f2ceaf39a9","row":{"name":"test","type":"internal"},"op":"insert","table":"Interface"},{"where":[["_uuid","==",["uuid","d3d393e2-d5b9-4b7e-bb91-071a53ccc6ab"]]],"row":{"bridges":["set",[["named-uuid","row1fac7c5f_0e62_499b_bb92_98fb3412a270"],["uuid","407f3645-862e-4ac0-98ae-7a46cfdaa4ec"],["uuid","d40ac0ea-e7d9-4ab1-83c5-168bdc45c6ba"],["uuid","f779e141-0ac0-4b38-8b61-50e199ea1da8"]]]},"op":"update","table":"Open_vSwitch"},{"uuid-name":"row9a846cad_8684_4c3d_9679_c4a30e1f8f28","row":{"name":"test","interfaces":["named-uuid","rowaf607491_b948_40a9_8fa3_52f2ceaf39a9"]},"op":"insert","table":"Port"},{"uuid-name":"row1fac7c5f_0e62_499b_bb92_98fb3412a270","row":{"name":"test","ports":["named-uuid","row9a846cad_8684_4c3d_9679_c4a30e1f8f28"]},"op":"insert","table":"Bridge"},{"mutations":[["next_cfg","+=",1]],"where":[["_uuid","==",["uuid","d3d393e2-d5b9-4b7e-bb91-071a53ccc6ab"]]],"op":"mutate","table":"Open_vSwitch"},{"where":[["_uuid","==",["uuid","d3d393e2-d5b9-4b7e-bb91-071a53ccc6ab"]]],"columns":["next_cfg"],"op":"select","table":"Open_vSwitch"},{"comment":"ovs-vsctl (invoked by -bash): ovs-vsctl -v add-br test","op":"comment"}], id=2
``` 

*其中数据部分可以用 json 解释器来看*

根据 `id=2` 我们还可以提起回复信息：

```
2017-07-21T16:33:33Z|00015|jsonrpc|DBG|unix:/var/run/openvswitch/db.sock: received reply, result=[{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{"uuid":["uuid","c15e7fc8-ab1c-46c8-b8d2-da516b90e7e0"]},{"count":1},{"uuid":["uuid","2d0ab4e5-a596-4214-ad1d-94389a160f16"]},{"uuid":["uuid","f6bf6a3f-a3d4-49e2-b06a-ba43c2431a4c"]},{"count":1},{"rows":[{"next_cfg":128}]},{}], id=2
```

在 idl 中，我们看到了只有数据库的同步操作，但是没有数据库的修改操作。

这个 `Transaction` 就是用来完成修改操作的。

```
    # Status values that Transaction.commit() can return.
    UNCOMMITTED = "uncommitted"  # Not yet committed or aborted.
    UNCHANGED = "unchanged"      # Transaction didn't include any changes.
    INCOMPLETE = "incomplete"    # Commit in progress, please wait.
    ABORTED = "aborted"          # ovsdb_idl_txn_abort() called.
    SUCCESS = "success"          # Commit successful.
    TRY_AGAIN = "try again"      # Commit failed because a "verify" operation
                                 # reported an inconsistency, due to a network
                                 # problem, or other transient failure.  Wait
                                 # for a change, then try again.
    NOT_LOCKED = "not locked"    # Server hasn't given us the lock yet.
    ERROR = "error"              # Commit failed due to a hard error.****
```

### `def __init__(self, idl)`

```
    def __init__(self, idl):
        """Starts a new transaction on 'idl' (an instance of ovs.db.idl.Idl).
        A given Idl may only have a single active transaction at a time.

        A Transaction may modify the contents of a database by assigning new
        values to columns (attributes of Row), deleting rows (with
        Row.delete()), or inserting rows (with Transaction.insert()).  It may
        also check that columns in the database have not changed with
        Row.verify().

        When a transaction is complete (which must be before the next call to
        Idl.run()), call Transaction.commit() or Transaction.abort()."""
        assert idl.txn is None

        idl.txn = self
        self._request_id = None
        self.idl = idl
        self.dry_run = False
        self._txn_rows = {}
        self._status = Transaction.UNCOMMITTED
        self._error = None
        self._comments = []

        self._inc_row = None
        self._inc_column = None

        self._fetch_requests = []

        self._inserted_rows = {}  # Map from UUID to _InsertedRow
```

* `_status`：该 transaction 的状态
* `_comments`：发送给 ovsdb server 的日志
* `_error`：当前的错误信息
* `_txn_rows`：每次插入新 raw 时就会在这个属性里面进行记录
* `_fetch_requests`：相当于 `monitor` 命令，提取数据库中的数据那些行
* `_inc_row` 增量 raw
* `_inc_column` 增量 column
* `dry_run`：所有的命令实际上并不执行，仅仅测试
* `_inserted_rows`：当有新的 raw 被插入时，记录该 raw 与执行 insert 命令的对应关系

调用示例：`txn.insert(self.api._tables['Manager'])`

### `def add_comment(self, comment)`

增加日志

### `def wait(self, poller)`

等待与 ovsdb 的交易完成

### `def get_error(self)`

获取当前的状态信息，若是当前状态为 `ERROR`，则通过 `self._error` 获取错误信息。

### `def __set_error_json(self, json)`

设置错误信息

### `def commit(self)`

1. 判断是否锁被别的进程占用
2. 若是设置了锁名称，则建立占有锁的命令
3. 增加等待命令。（解析：对于 bridge 来说，其依赖于 port，也就是必须要现有 port 的一个记录，才能创建 bridge）
4. 增加 raw 的删除、新建、更新命令
5. 增加 `fetch` 命令
6. 增加 `mutate` 和 `select` 命令
7. 增加 `commnet` 命令（记录到日志中）
8. 判断是否为测试命令
9. 若是 raw 没有任何改变，则不作操作；若是 raw 发生了变动，则将所有的命令发送出去。（所以，你只发送一个 comment 命令是不会被执行的）
10. 调用 `__disassemble` 意味着此次 idl 与 ovsdb server 的交易结束

### `def __disassemble(self)`

交易结束（调用了 commit 方法）则会调用此方法。

在 idl 中取消与交易的关联，将交易中的 raw 置空。

### `def commit_block(self)`

只要交易的状态一直是 `INCOMPLETE`，则一直阻塞执行 commit 和 idl.run 方法

### `def insert(self, table, new_uuid=None)`

在 table 中插入一个新的记录( raw )。

### `def _write(self, row, column, datum)`

改变 raw 的数据（删除、变更）。

### `def _fetch(self, row, column_name)`

在 `_fetch_requests` 中增加需要执行 fetch 命令的 raw 及其 column

```
    def _fetch(self, row, column_name):
        self._fetch_requests.append({"row":row, "column_name":column_name})
```

### `def _increment(self, row, column)`

```
    def _increment(self, row, column):
        assert not self._inc_row
        self._inc_row = row
        self._inc_column = column
```

增加需要执行 `mutate` 和 `select` 命令的 raw

### `def get_insert_uuid(self, uuid)`

raw 中的 uuid 是实际数据库中的 uuid 是不同的。本方法就是通过 raw 的 uuid 获取 实际数据库中的 uuid

### `def abort(self)`

终止当前的交易

### `def _process_reply(self, msg)`

处理 ovsdb server 给的回复

1. 检查所有的回复中是否含有 error 信息
2. 若存在 `_inc_row`，则调用 `__process_inc_reply` 检查与 inc 相关的回复是否符合规定
3. 若存在 `_fetch_requests`，则调用 `__process_fetch_reply` 检查与 fetch 相关的回复是否合法
4. 若存在 `_inserted_rows`，则调用 `__process_insert_reply` 检查与 insert 相关的回复是否合法
5. 在所有的检查完成后，设定这次交易完成的 state 

## `class Row(object)`

代表着 ovsdb 数据库中的一条记录

```
    def __init__(self, idl, table, uuid, data):
        # All of the explicit references to self.__dict__ below are required
        # to set real attributes with invoking self.__getattr__().
        self.__dict__["uuid"] = uuid

        self.__dict__["_idl"] = idl
        self.__dict__["_table"] = table

        # _data is the committed data.  It takes the following values:
        #
        #   - A dictionary that maps every column name to a Datum, if the row
        #     exists in the committed form of the database.
        #
        #   - None, if this row is newly inserted within the active transaction
        #     and thus has no committed form.
        self.__dict__["_data"] = data

        # _changes describes changes to this row within the active transaction.
        # It takes the following values:
        #
        #   - {}, the empty dictionary, if no transaction is active or if the
        #     row has yet not been changed within this transaction.
        #
        #   - A dictionary that maps a column name to its new Datum, if an
        #     active transaction changes those columns' values.
        #
        #   - A dictionary that maps every column name to a Datum, if the row
        #     is newly inserted within the active transaction.
        #
        #   - None, if this transaction deletes this row.
        self.__dict__["_changes"] = {}

        # A dictionary whose keys are the names of columns that must be
        # verified as prerequisites when the transaction commits.  The values
        # in the dictionary are all None.
        self.__dict__["_prereqs"] = {}
```

* `data` 存放着该记录当前的数据
* `_changes` 存放着更改的数据，这些数据还未写入到 server 数据库中
* `_prereqs` 存放着需要验证的数据，若是该条记录发生改变时，需要先验证这个属性存不存在。
