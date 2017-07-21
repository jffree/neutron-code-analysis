# Neutron Ovs Connection

*neutron/agent/ovsdb/native/connective.py*

## `class TransactionQueue(Queue.Queue, object)`

在队列的基础上封装了管道

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

1. 调用了 `idl.run` 方法，同步了 ovsdb server 的数据
2. 调用 `txn.do_commit` 和 `txn.results.put` 方法，实现了与 ovsdb server 的交易（创建、删除数据）操作。