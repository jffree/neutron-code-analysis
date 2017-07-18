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