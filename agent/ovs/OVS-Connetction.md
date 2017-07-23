# Neutron Ovs Connection

*neutron/agent/ovsdb/native/connective.py*

## `class TransactionQueue(Queue.Queue, object)`

在队列的基础上封装了管道（为了可以监听管道描述符的状态，发现有数据的写入和读取，这样子就可以知道队列中数据的写入和读取）。

```
    def __init__(self, *args, **kwargs):
        super(TransactionQueue, self).__init__(*args, **kwargs)
        alertpipe = os.pipe()
        # NOTE(ivasilevskaya) python 3 doesn't allow unbuffered I/O. Will get
        # around this constraint by using binary mode.
        self.alertin = os.fdopen(alertpipe[0], 'rb', 0)
        self.alertout = os.fdopen(alertpipe[1], 'wb', 0)
```

建立管道的的读写两端

### `def get_nowait(self, *args, **kwargs)`

从队列读出一个值的同时从管道中读取一个值

### `def put(self, *args, **kwargs)`

放入队列中数据的同时，在管道中写一个 `X`

### `def alert_fileno(self)`

属性方法，获取写管道的文件描述符

## `class Connection(object)`

```
    def __init__(self, connection, timeout, schema_name, idl_class=None):
        self.idl = None
        self.connection = connection
        self.timeout = timeout
        self.txns = TransactionQueue(1)
        self.lock = threading.Lock()
        self.schema_name = schema_name
        self.idl_class = idl_class or idl.Idl
```

* `connection`：如何连接到 ovsdb（默认为：`'tcp:127.0.0.1:6640'`）
* `timeout`：执行 ovs-vsctl 命令的超时时间
* `schema_name`：OVSDB 中数据库的名称
* `idl_class`：默认为：`ovs.db.idl.Idl`

### `def queue_txn(self, txn)`

```
    def queue_txn(self, txn):
        self.txns.put(txn)
```

将一个 txn 放入队列中
 
### `def start(self, table_name_list=None)`

1. 与 ovsdb 建立连接，获取数据库的 schema
2. 根据 schema 构建 idl，并且获取 ovsdb 数据库中的数据
3. 开启一个线程，来运行 `self.run` 方法

### `def run(self)`

这个方法很重要。

1. `run` 方法是以一个单独的线程来运行的。 `run` 方法中会阻塞监听 `self.txns.alert_fileno` 管道是否有数据写入（当调用 `queue_txn` 就会向里面写入数据）。
2. 若发现有数据写入，则会先执行 `idl.run` 与 ovsdb 的数据库进行一次同步操作。然后读取在队列中写入的数据（实际上这里写入的数据会是一个 `NeutronOVSDBTransaction` 的实例，在 `NeutronOVSDBTransaction.commit` 方法中）。
3. 读取到 `NeutronOVSDBTransaction` 的实例后，会执行 `NeutronOVSDBTransaction` 中的命令（`do_commit`），并且将结果保存起来
4. 最后再调用 `NeutronOVSDBTransaction.task_done` 方法