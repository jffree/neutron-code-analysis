# OVS REDAME

版本 2.5.0

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

## 有限状态机 FSM

* Reconnect 定义了五种连接状态，分别是：`Void`、`Listening`、`Backoff`、`ConnectInProgress`、`Active`、`Idle`、`Reconnect`。每个状态都有如下属性：
 1. `name`：该状态的名称
 2. `is_connected`：该状态中是否进行的了网络连接
 3. `deadline`：该状态的失效时间
 4. `run`：FSM 的下一步动作

## Stream

这个模块负责 socket 连接的维护。

* `Stream` 这个类负责与建立与 server 端的 socket 连接，并可以发送和接受消息
* `PassiveStream` 这个类负责建立监听，并可以接受连接。

## RPC（jsonrpc 模块）

* `Message` 负责封装与 OVSDB 通信的消息
 1. `type_` 表示消息的类型
 2. `method` 表示调用 OVSDB 的什么方法
 3. `params` 表示给调用方法传递的参数
 4. `result` 表示 ovsdb 返回的执行结果
 5. `error` 表示 ovsdb 返回的错误代码
 6. `id` 表示这次请求的 id

* `Connection` 实现与 ovsdb 的通信
 1. 维护一个 `Stream` 对象，来建立与 ovsdb 的连接
 2. 将 `Message` 格式的消息解封装，发送到 ovsdb
 3. 将从 ovsdb 接收的消息用 `Message` 封装

* `Session` 
 1. 一个集合了 RPC、Stream、PassiveStream、Reconnect 的回话管理类

## Schema and Types

这两个模块描述了整个 ovsdb 的数据库结构

1. `DbSchema` 描述数据库，其 `tables` 属性代表着数据库内的表结构
2. `TableSchema` 用来描述数据库中的表，每一个表都有多个 column
3. `ColumnSchema` 用来描述数据库中的 column，每个 column 都有一个 type 属性
4. `Type` 用来描述 column 中的 type，每个 type 都会有一个 key 属性
5. `BaseType` 用来描述 type 中的 key 属性

## IDL 

*Open vSwitch Database Interface Definition Language (OVSDB IDL)*

与 ovsdb server 进行通信的最高层次的封装，集合了上面几个模块的所有功能。

将 ovsdb server 中保存的数据库映射到内存中来，并且对 ovsdb server 的数据库进行实时的检测，随时更新内存中的数据库

1. 维护了一个 session 负责与 ovsdb server 进行通信
2. 封装了监听 ovsdb table 的方法，封装了获取 ovsdb lock 的方法。
3. 维护了一个 tables 变量，里面存放着与 ovsdb 中相同的表结构以及数据记录
4. table 中用 `Raw` 来封装每一条的记录

## Transaction

IDL 负责读取 ovsdb 的数据，而 Transact 负责写入数据

## 参考

[Openvswitch手册(1): 架构，SSL, Manager, Bridge](http://www.cnblogs.com/popsuper1982/p/3800574.html)
