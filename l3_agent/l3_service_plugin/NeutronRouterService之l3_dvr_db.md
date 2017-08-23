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

### `def _get_dvr_sync_data(self, context, host, agent, router_ids=None, active=None)`

1. 调用 `L3_NAT_dbonly_mixin._get_router_info_list` 获取与 router_ids 所代表的 router 有关的详细数据（包含 port 和 floating ip）
2. 获取 distributed router 的 id，获取与 distributed router 绑定的 floating ip
3. 若是含有 与 distributed router 绑定的 floating ip，则：
 1. 调用 `core_plugin.get_ports` 获取与这些 floating ip 绑定的 port
 2. 获取那些与该 host 绑定的 port，或者将要迁移到该 host 上的 port
 3. 若是上一步获取的 port绑定了 floating ip
  1. 调用 `_get_dvr_service_port_hostid` 获取提供 dvr 服务的 port 的 host_id 属性
  2. 调用 `_get_dvr_migrating_service_port_hostid` 获取提供 dvr 服务的 port 准备迁移到的 host 的 id
 4. 调用 `_process_routers` 为 router 数据填充 `_snat_router_interfaces` 属性
 5. 调用 `_process_floating_ips_dvr`






### `def _build_routers_list(self, context, routers, gw_ports)`

1. 查询数据库 `RouterL3AgentBinding` 获取所有与 routers 有关的绑定记录
2. 完善各个 router 的数据（添加 `gw_port_id`、`gw_port`、`enable_snat`、`gw_port_host` 属性）

### `def _get_dvr_service_port_hostid(self, context, port_id, port=None)`

若是该 port 是用来提供 dvr 服务的，则返回该 port 的 host_id 属性

### `def _get_dvr_migrating_service_port_hostid(self, context, port_id, port=None)`

若该 port 是用来提供 dvr 服务的，则检查该 port 是否准备迁移到一个 host 上，若是的话则返回该 host 的 Id

### `def _process_routers(self, context, routers)`

1. 调用 `_get_snat_sync_interfaces` 获取用于提供 snat 服务的 port 的数据信息
2. 为所有的 router 数据填充 `_snat_router_interfaces` 属性

### `def _get_snat_sync_interfaces(self, context, router_ids)`

获取用于提供 snat 服务的 port 的数据信息

### `def _process_floating_ips_dvr(self, context, routers_dict, floating_ips, host, agent)`

















