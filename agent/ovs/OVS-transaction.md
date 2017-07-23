# neutron ovs transaction

## `class Transaction(object)`

*neutron/agent/ovsdb/api.py*

抽象基类


```
@six.add_metaclass(abc.ABCMeta)
class Transaction(object):
    @abc.abstractmethod
    def commit(self):
        """Commit the transaction to OVSDB"""

    @abc.abstractmethod
    def add(self, command):
        """Append an OVSDB operation to the transaction"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is None:
            self.result = self.commit()
```

最重要的方法：`__enter__` 和 `__exit__`，当我们以 `with` 的方式调用 `Transaction` 时，就是调用这两个方法。

在 `__exit__` 中，我们可以看到，若是没有错误的情况下，会执行 `commit` 方法。也就是会在 `commit` 方法中执行 ovs 命令。

## `class Transaction(api.Transaction)`

*neutron/ageng/ovsdb/impl_idl.py*

```
    def __init__(self, api, ovsdb_connection, timeout,
                 check_error=False, log_errors=True):
        self.api = api
        self.check_error = check_error
        self.log_errors = log_errors
        self.commands = []
        self.results = Queue.Queue(1)
        self.ovsdb_connection = ovsdb_connection
        self.timeout = timeout
        self.expected_ifaces = set()
```

* `api`：`OvsdbIdl` 的实例
* `check_error`：命令执行出错时，是否引发异常
* `log_errors`：是否需要在 log 中记录错误信息
* `commands`：需要执行的命令
* `results`：大小为 1 的队列，存放命令的执行结果
* `ovsdb_connection`：`Connection` 的实例，用于与 ovsdb 通信
* `timeout`：命令执行的超时时间
* `expected_ifaces`：本次交易完成后，希望在 ovsdb 数据库中出现的 Interface 接口（在这个变量每次交易前都会清空（在 `pre_commit` 方法中），在交易的过程中（`command.run_idl`）可能会被设置，在交易完成后（`post_commit`）中会做检查）

### `def add(self, command)`

在 `commands` 中增加命令

### `def commit(self)`

这个方法很简单，它将实例自身放在 `ovsdb_connection` 的队列中，这样会触发队列的读操作（请参考 `Connection.run` 命令），进而会执行 `do_commit` 和 `task_done` 命令。

### `def do_commit(self)`

1. 创建一个 `idl.Transaction` 实例，用于执行 ovsdb 的 transact 指令。
2. 执行 `pre_commit` 命令
3. 调用所有命令的 `run_idl` 方法（这个方法请参考 `command` 模块，其实就是对要做出改变的 raw 进行操作）
4. 调用 `txn.commit_block` 方法，这个方法会一直阻塞，知道与 ovsdb server 的交易完成，也就是将上一步对 raw 的改变写入到数据库中。
5. 根据与 ovsdb server 交易的结果进行不同的处理
 1. 交易结果为 `TRY_AGAIN`，则会调用 `idlutils.wait_for_change` 等待交易结束或者超时
 2. 交易结果为 `ERROR`，则会记录错误，引发异常
 3. 交易结果为 `ABORTED`，则会直接退出
 4. 交易结果为 `UNCHANGED`，不做任何操作
 5. 交易结果为 `SUCCESS`，则会调用 `post_commit` 方法
6. 最后返回所有命令的执行结果

### `def timeout_exceeded(self)` 

判断命令执行是否超时

### `def pre_commit(self, txn)`

在子类 `NeutronOVSDBTransaction` 中实现

### `def post_commit(self, txn)`

在子类 `NeutronOVSDBTransaction` 中实现

### `def elapsed_time(self)`

本次交易中，命令执行的时间

### `def time_remaining(self)`

本次交易完成的剩余时间

## `class NeutronOVSDBTransaction(Transaction)`

### `def pre_commit(self, txn)`

```
    def pre_commit(self, txn):
        self.api._ovs.increment('next_cfg')
        txn.expected_ifaces = set()
```

指定一个自增的 column：`next_cfg`

*client request id: 也即cur_cfg和next_cfg，当一个client修改了数据库的之后，增加next_cfg，然后等待openvswitch应用这些修改，当修改应用完毕，则cur_cfg = next_cfg。如果我们打开/etc/openvswitch/conf.db文件，我们发现，随着我们队openvswitch的配置，cur_cfg是不断++的 *

### `def post_commit(self, txn)`

调用 `do_post_commit` 方法

### `def do_post_commit(self, txn)`

1. 调用 `vswitchd_has_completed` 确认 ovsdb server 端的操作已经执行完毕，若是超时则会引发异常
2. 调用 `post_commit_failed_interfaces` 检查希望创建的 interface 是否都已经创建完成，若是未创建完成则会引发异常

### `def vswitchd_has_completed(self, next_cfg)`

```
    def vswitchd_has_completed(self, next_cfg):
        return self.api._ovs.cur_cfg >= next_cfg
```

cur_cfg >= netx_cfg 则意味着在 ovsdb server 处理已经完成

### `def post_commit_failed_interfaces(self, txn)`

检查希望创建的 interface 是否都已经创建完成

