# Neutron 中对 ovs 封装的总结

经过封装后的 ovs 执行一条命令的流程为：

1. 创建一个 command 实例（例如：`AddManagerCommand`）
2. 执行 command 实例的 `execute` 方法，在该方法中会做下面几个事情：
 1. 以 `with` 的方式创建一个 transaction 实例（`NeutronOVSDBTransaction`），这样子，就会执行 transaction 的 `__enter__` 方法
 2. 将自身增加在 transaction 实例中（`commands`属性）。
 3. `with` 结束，会调用 transaction 实例的 `__exit__` 方法，该方法里面调用了 transaction 实例的 `commit` 方法
3. transaction 实例的 commit 方法，调用了 connnection 对象（`Connection`）的 `queue_txn` 方法，将自身放在了 connection 对象的队列中。
4. 由于 connetion 对象的 `run` 方法一直在监听自身的队列，所以当有数据放进去的时候，会立即在 `run` 方法中取出，并执行取出的 transaction 实例的 `do_commit` 方法。
5. transaction 实例的 `do_commit` 方法，这个方法做了如下几个事情：
 1. 构造一个 `idl.Transaction` 实例
 2. 调用 `pre_commit` 方法，做一些交易前的预处理
 3. 调用 `commands` 属性中所有方法的 `run_idl` 方法。每个 command 对象都会实现 `run_idl` 方法，这个方法里面会实现自身命令需要完成的动作（也就是对数据库的修改）。
 4. 调用 `idl.Transaction` 实例的 `commit_block` 方法，完成与 ovsdb server 的数据库的交易，将所有的改变都写入 server 端的数据库中。
 5. 处理交易的结果

## Connection

1. 负责维护与 ovsdb server 的链接
2. 负责位于 ovs idl
3. 利用管道检查需要执行的交易，若有交易需要执行，则执行与 ovsdb 的交易

## `NeutronOVSDBTransaction`

* 对 ovs transaction 的封装。
 1. 收集需要执行的命令
 2. 执行与 ovsdb 的交易
 3. 检查与 ovsdb 交易的结果
 4. 返回与 ovsdb 交易的结果

## command

这个模块里面有很多的类，每个类对应着一个 ovs 命令，同时每个类都有一个 `run_idl` 这个里面完成了与 ovsdb 的真正交易

## OvsdbIdl

neutron 中 ovs 的 Idl。这个类综合了上述几个模块的功能，并在此基础上提供了一个更方便调用的接口。