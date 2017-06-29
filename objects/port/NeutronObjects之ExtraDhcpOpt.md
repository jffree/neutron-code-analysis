# Neutron object 之 ExtraDhcpOpt

*neutron/objects/port/extra_dhcp_opy.py*

## `class ExtraDhcpOpt(base.NeutronDbObject)`

```
@obj_base.VersionedObjectRegistry.register
class ExtraDhcpOpt(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = models.ExtraDhcpOpt

    fields = {
         'id': obj_fields.UUIDField(),
         'port_id': obj_fields.UUIDField(),
         'opt_name': obj_fields.StringField(),
         'opt_value': obj_fields.StringField(),
         'ip_version': obj_fields.IntegerField(),
    }
```