# Neutron objects 之 SubnetPool

*neutron/objects/subnetpool.py*

```
@obj_base.VersionedObjectRegistry.register
class SubnetPool(base.NeutronDbObject)
```

这里会注册 subnetpool 这个对象

## `class SubnetPool(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'
    db_model = models.SubnetPool
    fields = {
        'id': obj_fields.UUIDField(),
        'tenant_id': obj_fields.StringField(nullable=True),
        'name': obj_fields.StringField(nullable=True),
        'ip_version': common_types.IPVersionEnumField(),
        'default_prefixlen': common_types.IPNetworkPrefixLenField(),
        'min_prefixlen': common_types.IPNetworkPrefixLenField(),
        'max_prefixlen': common_types.IPNetworkPrefixLenField(),
        'shared': obj_fields.BooleanField(),
        'is_default': obj_fields.BooleanField(),
        'default_quota': obj_fields.IntegerField(nullable=True),
        'hash': obj_fields.StringField(nullable=True),
        'address_scope_id': obj_fields.UUIDField(nullable=True),
        'prefixes': common_types.ListOfIPNetworksField(nullable=True)
    }
    fields_no_update = ['id', 'tenant_id']
    synthetic_fields = ['prefixes']
```

### `def get_object(cls, context, **kwargs)`

* 这里的 `**kwargs` 一般指的是过滤选项

1. 构造 session
2. 调用 `super(SubnetPool, cls).get_object`，也就是 `NeutronDbObject.get_object`