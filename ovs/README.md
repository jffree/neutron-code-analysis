# OVS REDAME

## OVSDB

1. ovsdb-sever 是一个 ovs 数据库的守护进程，我们可以通过 JSON-RPC 来与之进行通信（ovs-vswitchd 也是通过这种方式来与 ovsdb-sever 进行通信的）。
2. 数据库中有一个叫做 `Open_vSwitch` 的数据库，其 schema 就是这个数据库中包含的表格，表格中包含的列。
3. 一个数据库下可以有很多表格，被称为 `tables`
4. 每个 `table` 可以有两个属性 
 1. `columns`：这个属性里面有很多的字段，用来存储该表格的数据
 2. `indexes`：这个字段表示 table 可以用什么来索引
5. 每个 `column` 可能会有三个字段：
 1. `mutable`：可变的
 2. `ephemeral`：短暂的
 3. `type`
6. 每个 `type` 都可能包含四个属性：
 1. `key`
 2. `value`
 3. `min`
 4. `max`
7. `key` 可能有如下几种类型：
 1. `void`
 2. `integer` 可能包含 `minInteger` 和 `maxInteger` 属性
 3. `real` 可能包含 `minReal` 和 `maxReal` 属性
 4. `boolean`
 5. `string` 可能会包含两个属性：`minLength` 和 `maxLength`
 6. `uuid` 会包含 `refType` 属性