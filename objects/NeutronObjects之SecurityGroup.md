# Neutron objects 之 `SecurityGroup`、 `_DefaultSecurityGroup` 和 `SecurityGroupRule`

*neutron/objects/securitygroup.py*

`SecurityGroup` 是父 object，与 `SecurityGroupRule` 是一对多的关系，与 `_DefaultSecurityGroup` 是一对一的关系

## `class SecurityGroup(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = sg_models.SecurityGroup

    fields = {
        'id': obj_fields.UUIDField(),
        'name': obj_fields.StringField(nullable=True),
        'project_id': obj_fields.StringField(nullable=True),
        'is_default': obj_fields.BooleanField(default=False),
        'rules': obj_fields.ListOfObjectsField(
            'SecurityGroupRule', nullable=True
        ),
        # NOTE(ihrachys): we don't include source_rules that is present in the
        # model until we realize it's actually needed
    }

    fields_no_update = ['project_id', 'is_default']

    synthetic_fields = ['is_default', 'rules']

    extra_filter_names = {'is_default'}
```

### `def from_db_object(self, db_obj)`

重写父类的该方法，判断该安全组是否为默认安全组

### `def create(self)`

重写父类的该方法，若创建的安全组为默认安全组，则需要创建默认安全组的数据库记录。

## `class _DefaultSecurityGroup(base.NeutronDbObject)`

```
@obj_base.VersionedObjectRegistry.register
class _DefaultSecurityGroup(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = sg_models.DefaultSecurityGroup

    fields = {
        'project_id': obj_fields.StringField(),
        'security_group_id': obj_fields.UUIDField(),
    }

    fields_no_update = ['security_group_id']

    primary_keys = ['project_id']
```

## `class SecurityGroupRule(base.NeutronDbObject)`

### 类属性

```
    VERSION = '1.0'

    db_model = sg_models.SecurityGroupRule

    fields = {
        'id': obj_fields.UUIDField(),
        'project_id': obj_fields.StringField(nullable=True),
        'security_group_id': obj_fields.UUIDField(),
        'remote_group_id': obj_fields.UUIDField(nullable=True),
        'direction': common_types.FlowDirectionEnumField(nullable=True),
        'ethertype': common_types.EtherTypeEnumField(nullable=True),
        'protocol': common_types.IpProtocolEnumField(nullable=True),
        'port_range_min': common_types.PortRangeField(nullable=True),
        'port_range_max': common_types.PortRangeField(nullable=True),
        'remote_ip_prefix': obj_fields.IPNetworkField(nullable=True),
    }

    foreign_keys = {'SecurityGroup': {'security_group_id': 'id'}}

    fields_no_update = ['project_id', 'security_group_id']
```

### `def modify_fields_to_db(cls, fields)`

### `def modify_fields_from_db(cls, db_obj)`

这两个方法都增加了对 `remote_ip_prefix` 的处理。