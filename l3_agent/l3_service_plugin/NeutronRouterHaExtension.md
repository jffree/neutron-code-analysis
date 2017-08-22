# Neutron Router ha extension

* extension : *neutron/extensions/l3_ext_ha_mode.py*

## 数据库

```
class L3HARouterAgentPortBinding(model_base.BASEV2)

class L3HARouterNetwork(model_base.BASEV2, model_base.HasProjectPrimaryKey)

class L3HARouterVRIdAllocation(model_base.BASEV2)
```

## `class L3_HA_NAT_db_mixin(l3_dvr_db.L3_NAT_with_dvr_db_mixin, router_az_db.RouterAvailabilityZoneMixin)`

对 router ha extension逻辑业务的实现。

*neutron/db/l3_hamode_db.py*

```
    extra_attributes = (
        l3_dvr_db.L3_NAT_with_dvr_db_mixin.extra_attributes +
        router_az_db.RouterAvailabilityZoneMixin.extra_attributes + [
            {'name': 'ha', 'default': cfg.CONF.l3_ha},
            {'name': 'ha_vr_id', 'default': 0}])
```

```
    def __init__(self):
        self._verify_configuration()
        super(L3_HA_NAT_db_mixin, self).__init__()
```






### `def get_ha_router_port_bindings(self, context, router_ids, host=None)`

查询数据库 `L3HARouterAgentPortBinding` 获取某台机器 host 上 router_ids 上绑定的 ha port 










