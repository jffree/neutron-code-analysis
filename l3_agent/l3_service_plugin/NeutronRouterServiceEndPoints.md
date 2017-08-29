# Neutron Router Service RPC EndPoints

*neutron/api/rpc/handlers/l3_rpc.py*

## `class L3RpcCallback(object)`

```
target = oslo_messaging.Target(version='1.9')
```

```
    @property
    def plugin(self):
        if not hasattr(self, '_plugin'):
            self._plugin = manager.NeutronManager.get_plugin()
        return self._plugin

    @property
    def l3plugin(self):
        if not hasattr(self, '_l3plugin'):
            self._l3plugin = manager.NeutronManager.get_service_plugins()[
                plugin_constants.L3_ROUTER_NAT]
        return self._l3plugin
```

获取 core plugin 和 l3 plugin 实例

### `def get_router_ids(self, context, host)`

1. 若 l3 plugin 支持 l3_agent_scheduler，且 router 支持自动调度，则调用 `l3plugin.auto_schedule_routers` 调度 router，与该 host 绑定
2. 调用 `l3plugin.list_router_ids_on_host` 返回来 host 上的 router

### `def sync_routers(self, context, **kwargs)`

1. 若 l3 plugin 支持 l3_agent_scheduler，则调用 `l3plugin.list_active_sync_routers_on_active_l3_agent` 获取与该 host 上 l3 agent 绑定的 router
2. 若 l3 plugin 不支持 l3_agent_scheduler，则调用 `l3plugin.get_sync_data` 获取指定 router 的数据
3. 若 core plugin 支持 `binding`，则调用 `_ensure_host_set_on_ports` 保证 port 与 host 的绑定关系
4. 返回 router 数据

### `def _ensure_host_set_on_ports(self, context, host, routers)`

1. 若 router 拥有 gateway port，且 router 是 distributed，则：
 1. 获取 gateway port 绑定的 host
 2. 调用 `_ensure_host_set_on_port` 确保 gateway port 要与 gateway port host 绑定
 3. 调用 `_ensure_host_set_on_port` 确保该 router 上的 snat port 都要与该 host 绑定
2. 对于其他的情况，则将 gateway port 与该 host 绑定
3. 调用 `_ensure_host_set_on_port` 确保其他的 port 与该 host 绑定
4. 调用 `_ensure_host_set_on_port` 确保 ha interface 与该 phost 绑定

### `def _ensure_host_set_on_port(self, context, host, port, router_id=None, ha_router_port=False)`

1. 判断 port 是否绑定成功
2. 若 port 未与当前的 host 绑定：
 1. 若该 port 不是 ha router port，则调用 `plugin.update_port` 将 port 与该 host 绑定
 2. 若该 port 是 ha router port，且该 port 未绑定 host：
  1. 调用 `l3plugin.get_active_host_for_ha_router` 获取对于该 router 来说可绑定的 host
  2. 调用 `plugin.update_port` 将这个 port 与该 host 绑定 
3. 若该 port 是一个 dvr port，则调用 `core_plugin.update_distributed_port_binding` 更新这些 dvr Port 的绑定

### `def get_external_network_id(self, context, **kwargs)`

获取 external network id

### `def get_service_plugin_list(self, context, **kwargs)`

获取当前 neutron 的 service plugin

### `def update_floatingip_statuses(self, context, router_id, fip_statuses)`

1. 调用 `l3plugin.update_floatingip_status` 更新 floating ip 的 status
2. 调用 `l3plugin.get_floatingips` 获取 floating ip 上次绑定的 router 为该 router id，但是现在未绑定 router 的，同样更新其状态

### `def get_ports_by_subnet(self, context, **kwargs)`

获取 subnet 上的 port

### `def get_agent_gateway_port(self, context, **kwargs)`

1. 调用 `l3plugin.create_fip_agent_gw_port_if_not_exists` 确保当前 host 上存在有 agent gateway
2. 调用 `_ensure_host_set_on_port` 确保该 agent gateway port 与该 host 绑定

### `def delete_agent_gateway_port(self, context, **kwargs)`

调用 `l3plugin.delete_floatingip_agent_gateway_port` 删除该 agent gateway port

### `def process_prefix_update(self, context, **kwargs)`

更新 subnet 的 cidr 属性

### `def update_ha_routers_states(self, context, **kwargs)`

调用 `l3plugin.update_routers_states` 实现 router status 的更新