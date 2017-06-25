# Neutron objects 之 `SubnetPool` 和 `SubnetPoolPrefix`

*neutron/objects/subnetpool.py*

**`SubnetPoolPrefix` object 是 `SubnetPool` object 的子对象，而且是多对一的关系**

## `class SubnetPoolPrefix(base.NeutronDbObject)`

```
@obj_base.VersionedObjectRegistry.register
class SubnetPoolPrefix(base.NeutronDbObject)
```

注册 `SubnetPoolPrefix` object 类

### 类属性

```
    VERSION = '1.0'
    db_model = models.SubnetPoolPrefix
    fields = {
        'subnetpool_id': obj_fields.UUIDField(),
        'cidr': obj_fields.IPNetworkField(),
    }
    primary_keys = ['subnetpool_id', 'cidr']
```

### `def modify_fields_to_db(cls, fields)`

类方法，重写了 `NeutronDbObject` 中的 `modify_fields_to_db`

调用 `filter_to_str` 将 cidr 的 field 值转换为字符串格式

### `def modify_fields_from_db(cls, db_obj)`

类方法，重写了 `NeutronDbObject` 中的 `modify_fields_from_db`

将 cidr 的 field 值转换为 `IPNetwork` 类型

## `class SubnetPool(base.NeutronDbObject)`

```
@obj_base.VersionedObjectRegistry.register
class SubnetPool(base.NeutronDbObject)
```

这里会注册 subnetpool 这个对象

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

### `def modify_fields_from_db(cls, db_obj)`

类方法，重写了 `NeutronDbObject` 中的 `modify_fields_from_db`

将 `prefixes` field 以 `netaddr.IPNetwork` 来表述

### `def modify_fields_to_db(cls, fields)`

类方法，重写了 `NeutronDbObject` 中的 `modify_fields_to_db`

将 `prefixes` field 以 `SubnetPoolPrefix` 来表述

### `def reload_prefixes(self)`

重新加载 `prefixes` field

用 `SubnetPoolPrefix` 对象的 `cidr` field 来做 prefixes field

### `def get_object(cls, context, **kwargs)`

* 这里的 `**kwargs` 一般指的是过滤选项

1. 构造 session
2. 调用 `super(SubnetPool, cls).get_object`，也就是 `NeutronDbObject.get_object`
3. 调用 `reload_prefixes` 来重新构造 `prefixes` field

### `def get_objects(cls, context, _pager=None, validate_filters=True, **kwargs)`

与 `get_object` 方法类似，也是对所有的 object 调用了一遍 `reload_prefixes` 方法

### `def create(self)`

在创建一个 subnetpool 的对象时，会创建一个 subnetpool 的数据库记录。

在创建过程中，若发现了 `prefixes` field 发生改动的话，则同时会创建与之相关联的 subnetpoolprefixes 数据库记录

### `def update(self)`

在更新一个 subnetpool 的对象时，会更新与之相匹配的 subnetpool 的数据库记录。

在更新过程中，若发现了 `prefixes` field 发生改动的话，则同时会删除与旧 subnetpool object 相关联的 subnetpoolprefixes 数据库记录，创建新的 subnetpoolprefixes 数据库记录。




 