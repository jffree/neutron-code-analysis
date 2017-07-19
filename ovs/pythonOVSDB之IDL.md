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

ovsdb 的 database schema 的获取有两种方法：一个是通过 JSON-RPC 从 ovsdb 中读取（也就是 schema_json），另外一个是从 schema 文件中读取（location 代表了文件的位置）。

### `def get_idl_schema(self)`




## `class Idl(object)`

将 ovsdb 中的数据库拿到内存中来处理。
















