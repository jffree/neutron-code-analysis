# Neutron object 之 Subnet 

*neutron/objects/subnet.py*

Subnet object 下面有三个子 object：`DNSNameServer`、`Route`、`IPAllocationPool`，我们先从这三个子 object 看起。

## `class DNSNameServer(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = models_v2.DNSNameServer

    primary_keys = ['address', 'subnet_id']

    foreign_keys = {'Subnet': {'subnet_id': 'id'}}

    fields = {
        'address': obj_fields.StringField(),
        'subnet_id': obj_fields.UUIDField(),
        'order': obj_fields.IntegerField()
    }
```

### `def get_objects(cls, context, _pager=None, validate_filters=True, **kwargs)`

增加了默认分页排序的功能

## `class Route(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = models_v2.SubnetRoute

    primary_keys = ['destination', 'nexthop', 'subnet_id']

    foreign_keys = {'Subnet': {'subnet_id': 'id'}}

    fields = {
        'subnet_id': obj_fields.UUIDField(),
        'destination': common_types.IPNetworkField(),
        'nexthop': obj_fields.IPAddressField()
    }
```

### `def modify_fields_from_db(cls, db_obj)`

### `def modify_fields_to_db(cls, fields)`

增加了对 `destination` 和 `nexthop` 的处理。

## `class IPAllocationPool(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = models_v2.IPAllocationPool

    foreign_keys = {'Subnet': {'subnet_id': 'id'}}

    fields_need_translation = {
        'start': 'first_ip',
        'end': 'last_ip'
    }

    fields = {
        'id': obj_fields.UUIDField(),
        'subnet_id': obj_fields.UUIDField(),
        'start': obj_fields.IPAddressField(),
        'end': obj_fields.IPAddressField()
    }
```

### `def modify_fields_from_db(cls, db_obj)`

增加了对 `start` 和 `end` 的处理。

### `def modify_fields_to_db(cls, fields)`

增加了对 `first_ip` 和 `last_ip` 的处理。

## `class Subnet(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = models_v2.Subnet

    fields = {
        'id': obj_fields.UUIDField(),
        'project_id': obj_fields.StringField(nullable=True),
        'name': obj_fields.StringField(nullable=True),
        'network_id': obj_fields.UUIDField(),
        'segment_id': obj_fields.UUIDField(nullable=True),
        'subnetpool_id': obj_fields.UUIDField(nullable=True),
        'ip_version': common_types.IPVersionEnumField(),
        'cidr': common_types.IPNetworkField(),
        'gateway_ip': obj_fields.IPAddressField(nullable=True),
        'allocation_pools': obj_fields.ListOfObjectsField('IPAllocationPool',
                                                          nullable=True),
        'enable_dhcp': obj_fields.BooleanField(nullable=True),
        'shared': obj_fields.BooleanField(nullable=True),
        'dns_nameservers': obj_fields.ListOfObjectsField('DNSNameServer',
                                                         nullable=True),
        'host_routes': obj_fields.ListOfObjectsField('Route', nullable=True),
        'ipv6_ra_mode': common_types.IPV6ModeEnumField(nullable=True),
        'ipv6_address_mode': common_types.IPV6ModeEnumField(nullable=True)
    }

    synthetic_fields = ['allocation_pools', 'dns_nameservers', 'host_routes',
                        'shared']

    foreign_keys = {'Network': {'network_id': 'id'}}

    fields_no_update = ['project_id']

    fields_need_translation = {
        'project_id': 'tenant_id',
        'host_routes': 'routes'
    }
```

### `def __init__(self, context=None, **kwargs)`

```
    def __init__(self, context=None, **kwargs):
        super(Subnet, self).__init__(context, **kwargs)
        self.add_extra_filter_name('shared')
```

### `def obj_load_attr(self, attrname)`

增加了对 `shared` field 的处理

### `def _load_shared(self, db_obj=None)`

该方法即确定当前的客户（context）是否有权限（根据 rbac 规则）访问该 network。

若是当前租户有权限访问，则设置 `shared` field 为 true，否则设置为 False

### `def from_db_object(self, db_obj)`

增加对 `shared` field 的处理

### `def modify_fields_from_db(cls, db_obj)`

### `def modify_fields_to_db(cls, fields)`

这两个方法增加了对 `cidr` 和 `gateway_ip` 的处理