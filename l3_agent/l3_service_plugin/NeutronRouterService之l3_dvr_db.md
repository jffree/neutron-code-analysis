# Neutron Router Service 之 l3_dvr_db

*neutron/db/l3_dvr_db.py*

为 l3 router 增加 dvr 的处理

## `class L3_NAT_with_dvr_db_mixin(l3_db.L3_NAT_db_mixin, l3_attrs_db.ExtraAttributesMixin)`

```
    router_device_owners = (
        l3_db.L3_NAT_db_mixin.router_device_owners +
        (const.DEVICE_OWNER_DVR_INTERFACE,
         const.DEVICE_OWNER_ROUTER_SNAT,
         const.DEVICE_OWNER_AGENT_GW))

    extra_attributes = (
        l3_attrs_db.ExtraAttributesMixin.extra_attributes + [{
            'name': "distributed",
            'default': cfg.CONF.router_distributed
        }])
```
