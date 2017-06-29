# Neutron object 之 NetworkPortSecurity

*neutron/objects/network/port_security.py*

## `class NetworkPortSecurity(base_ps._PortSecurity)`

```
@obj_base.VersionedObjectRegistry.register
class NetworkPortSecurity(base_ps._PortSecurity):
    # Version 1.0: Initial version
    VERSION = "1.0"

    fields_need_translation = {'id': 'network_id'}

    db_model = models.NetworkSecurityBinding
```

## `class _PortSecurity(base.NeutronDbObject)`

*neutron/objects/extensions/port_security.py*

```
class _PortSecurity(base.NeutronDbObject):
    fields = {
        'id': obj_fields.UUIDField(),
        'port_security_enabled': obj_fields.BooleanField(
            default=portsecurity.DEFAULT_PORT_SECURITY),
    }
```