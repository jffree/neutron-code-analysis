# Nutron object 之 AllowedAddressPair

*neutron/objects/port/extensions/allowedaddresspairs.py*

## `class AllowedAddressPair(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = models.AllowedAddressPair

    primary_keys = ['port_id', 'mac_address', 'ip_address']

    fields = {
        'port_id': obj_fields.UUIDField(),
        'mac_address': common_types.MACAddressField(),
        'ip_address': common_types.IPNetworkField(),
    }
```

### `def modify_fields_to_db(cls, fields)`

### `def modify_fields_from_db(cls, db_obj)`

这两个方法增加了对 `ip_address` 和 `mac_address` 的处理。

