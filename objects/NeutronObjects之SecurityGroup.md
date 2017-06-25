# Neutron objects 之 `SecurityGroup`、 `_DefaultSecurityGroup` 和 `SecurityGroupRule`

*neutron/objects/securitygroup.py*

`SecurityGroup` 是父 object，与 `SecurityGroupRule` 是一对多的关系，与 `_DefaultSecurityGroup` 是一对一的关系

## `class SecurityGroup(base.NeutronDbObject)`

### `def from_db_object(self, db_obj)`

重写父类的该方法，判断该安全组是否为默认安全组

### `def create(self)`

重写父类的该方法，若创建的安全组为默认安全组，则需要创建默认安全组的数据库记录。