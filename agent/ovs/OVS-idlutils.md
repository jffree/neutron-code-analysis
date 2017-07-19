# Neutron Agent OvsDB 之 idlutils

*neutron/agent/ovsdb/native/idlutils.py*

## `def get_schema_helper(connection, schema_name)`

相当于执行 `ovsdb-client get-schema 'tcp:127.0.0.1:6640' 'Open_vSwitch'` 命令的操作。

然后用 `SchemaHelper` 封装命令的结果。





