# Neutron Agent OvsDB 之 idlutils

*neutron/agent/ovsdb/native/idlutils.py*

## `def get_schema_helper(connection, schema_name)`

相当于执行 `ovsdb-client get-schema 'tcp:127.0.0.1:6640' 'Open_vSwitch'` 命令的操作。

然后用 `SchemaHelper` 封装命令的结果。

## `def wait_for_change(_idl, timeout, seqno=None)`

ovs idl 在刚创建时，里面的 tables 是没有存储数据的，这个方法就是调用 `_idl.run` 方法来获取 ovsdb server 数据库中的数据。

## `def row_by_value(idl_, table, column, match, default=_NO_DEFAULT)`

查看 ovs 数据库中是否有符合 macth 的记录，若是有的话则返回该记录的 raw 实例。

* 参数说明：
 1. `idl_`：ovs IDL 实例。
 2. `table`：存储在 idl tables 中一个表的名称
 3. `column`：table 中的一条属性
 4. `match`：某一个记录。

## `def row_by_record(idl_, table, record)`

根据某一记录的值，查找到其对应的 raw。

该方法与 `row_by_value` 不同之处在于 `row_by_value` 指明了要在 table 中的哪个 column 中查找。

而 `row_by_record` 没有指明。所有 `row_by_record` 方法需要先查询在该表中可以查询的 column，然后调用 `row_by_value` 在该 `column` 中进行查找

## `def get_column_value(row, col)`

获取某一记录 raw 下某个 column 的值