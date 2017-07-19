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
    IDL_S_INITIAL = 0
    IDL_S_MONITOR_REQUESTED = 1
    IDL_S_MONITOR_COND_REQUESTED = 2

    def __init__(self, remote, schema):
        assert isinstance(schema, SchemaHelper)
        schema = schema.get_idl_schema()

        self.tables = schema.tables
        self.readonly = schema.readonly
        self._db = schema
        self._session = ovs.jsonrpc.Session.open(remote)
        self._monitor_request_id = None
        self._last_seqno = None
        self.change_seqno = 0
        self.uuid = uuid.uuid1()
        self.state = self.IDL_S_INITIAL

        # Database locking.
        self.lock_name = None          # Name of lock we need, None if none.
        self.has_lock = False          # Has db server said we have the lock?
        self.is_lock_contended = False  # Has db server said we can't get lock?
        self._lock_request_id = None   # JSON-RPC ID of in-flight lock request.

        # Transaction support.
        self.txn = None
        self._outstanding_txns = {}

        for table in six.itervalues(schema.tables):
            for column in six.itervalues(table.columns):
                if not hasattr(column, 'alert'):
                    column.alert = True
            table.need_table = False
            table.rows = {}
            table.idl = self
            table.condition = []
            table.cond_changed = False
```














