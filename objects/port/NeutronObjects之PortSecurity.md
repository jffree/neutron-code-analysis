# Neutron object 之 PortSecurity

*neutron/objects/port/port_security.py*

## `class PortSecurity(base_ps._PortSecurity)`

```
@obj_base.VersionedObjectRegistry.register
class PortSecurity(base_ps._PortSecurity):
    # Version 1.0: Initial version
    VERSION = "1.0"

    fields_need_translation = {'id': 'port_id'}

    db_model = models.PortSecurityBinding
```