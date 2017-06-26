# Neutron objects 之 NeutronRbacObject

*neutron/objects/rbac_db.py*

这个 Objcet 有点复杂，我们看看是怎么实现的：

```
NeutronRbacObject = with_metaclass(RbacNeutronMetaclass, base.NeutronDbObject)
```

## 元类：`class RbacNeutronMetaclass(type)`

### `def __new__(mcs, name, bases, dct)`

1. 调用 `validate_existing_attrs`