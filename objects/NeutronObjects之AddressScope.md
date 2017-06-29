# Neutron object 之 AddressScope

*neutron/objects/address_scope.py*

## `class AddressScope(base.NeutronDbObject)`

```
@obj_base.VersionedObjectRegistry.register
class AddressScope(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = models.AddressScope

    fields = {
        'id': obj_fields.UUIDField(),
        'tenant_id': obj_fields.StringField(nullable=True),
        'name': obj_fields.StringField(),
        'shared': obj_fields.BooleanField(),
        'ip_version': common_types.IPVersionEnumField(),
    }
```