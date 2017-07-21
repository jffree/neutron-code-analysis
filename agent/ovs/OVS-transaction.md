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


## `class Transaction(api.Transaction)`

*neutron/ageng/ovsdb/impl_idl.py*

## `class NeutronOVSDBTransaction(Transaction)`

















