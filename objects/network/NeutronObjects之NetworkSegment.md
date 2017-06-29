# Neutron object 之 NetworkSegment

*neutron/objects/network/network_segment.py*

## `class NetworkSegment(base.NeutronDbObject)`

```
@obj_base.VersionedObjectRegistry.register
class NetworkSegment(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = segment_model.NetworkSegment

    fields = {
        'id': obj_fields.UUIDField(),
        'network_id': obj_fields.UUIDField(),
        'name': obj_fields.StringField(),
        'network_type': obj_fields.StringField(),
        'physical_network': obj_fields.StringField(nullable=True),
        'segmentation_id': obj_fields.IntegerField(nullable=True),
        'is_dynamic': obj_fields.BooleanField(default=False),
        'segment_index': obj_fields.IntegerField(default=0)
    }

    foreign_keys = {'Network': {'network_id': 'id'}}
```