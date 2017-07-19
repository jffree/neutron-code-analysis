# Neutron Ovs Connection

*neutron/agent/ovsdb/native/connective.py*

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
 


