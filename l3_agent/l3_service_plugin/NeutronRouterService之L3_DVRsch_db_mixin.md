# Neutron Router Service 之 L3_DVRsch_db_mixin

*neutron/db/l3_dvrscheduler_db.py*

## `class L3_DVRsch_db_mixin(l3agent_sch_db.L3AgentSchedulerDbMixin)`

### `def get_subnet_ids_on_router(self, context, router_id)`

1. 调用 `core_plugin.get_ports` 获取该 router 上的 port
2. 获取这些 port 上所属的 subnet

### `def _check_dvr_serviceable_ports_on_host(self, context, host, subnet_ids)`

通过查询 `PortBinding`、`IPAllocation`、`Port` 数据库，查询该 host 上是否有属于 subnet_ids 的提供 dvr service 的 port
若有，则返回 True，没有则返回 False

### `def get_hosts_to_notify(self, context, router_id)`

1. 调用 `L3AgentSchedulerDbMixin.get_hosts_to_notify` 获取与该 router 绑定的 l3 agent 所在的 host
2. 若该 router 为 distributed 类型：
 1. 调用 `_get_dvr_hosts_for_router` 获取拥有该 dsitributed router 的 host
 2. 返回与该 router 有关系的所有 host

### `def _get_dvr_hosts_for_router(self, context, router_id)`

1. 调用 `get_subnet_ids_on_router` 获取与该 router 上绑定的 port 的 subnet
2. 通过查询数据库 `PortBinding`、`Port`、`IPAllocation` 获取这些 subnet 上用于提供 dvr 服务的 port 所在的 host

### `def get_dvr_routers_to_remove(self, context, deleted_port)`

1. 根据 port 的数据，获取其所在的 `host`、`subnet_id`
2. 调用 `get_dvr_routers_by_subnet_ids` 根据上面获得的 subnet_id 获取其上面提供 dvr 服务 port 所绑定的 router 
3. 调用 `_get_agent_by_type_and_host` 获取 port 所在 host 上的 l3 agent
4. 对于每一个 router：
 1. 查询数据库 `RouterL3AgentBinding` 查看 l3 agent 是否还与 router 绑定（**若一个 router 与一个 l3 agent 绑定，则意味着该 router 会在当前的 host 上提供 snat 服务**），若还在绑定则不对该 router 做任何处理
 2. 调用 `get_subnet_ids_on_router` 获取与该 router 有关的所有 subnet id
 3. 调用 `_check_dvr_serviceable_ports_on_host` 检查该 host 上是否存在需要 dvr 服务的 port，若是还有，则不对该 router 做任何处理
 4. 调用 `core_plugin.get_ports` 获取与该 router 绑定的所有提供 dvr 服务的 port
 5. 对于上一步获取的所有的 port，调用 `get_distributed_port_binding_by_host` 获取与当前 host 绑定的 dvr port，接触该 port 与 router 的绑定
 6. 记录将被删除 router 的信息 
返回所有将被删除的 router 的信息

解析：一个依赖于 dvr 服务的 port 删除后，可能会影响到该 port 所在 host 上的提供 dvr 服务的 router。

1. 若该 router 的存在只是为该 port 提供服务，那么该 port 在当前 host 上被删除则意味着提供 dvr 服务的 router 也无需再存在，需要删除。
2. 若该 router 的还需要为别的 port 提供 dvr 服务，则该 router 不应该被删除，通过以下判断可以得出该 router 是否还为别的 port 提供 dvr 服务：
 1. 若该 router 与当前 host 的 l3 agent 绑定，则意味着该 router 会在当前的 host 上提供 snat 服务，不应该被删除
 2. 若该 host 上还有别的 port 需要 dvr 服务，则也不应该删除该 router

### `def get_dvr_routers_by_subnet_ids(self, context, subnet_ids)`

1. 获取 subnet 上提供 dvr 服务的 port
2. 获取这些 port 所属的 router id

### `def dvr_handle_new_service_port(self, context, port, dest_host=None)`

1. 获取 port 将要绑定 host 上的 l3 agent
2. 调用 `check_for_fip_and_create_agent_gw_port_on_host_if_not_exists` 检查该 port 上是否挂有 floating ip，若有则创建 floating ip 所需要的网关
3. 调用 `get_dvr_routers_by_subnet_ids` 获取与 subnet 关联的 dvr router
4. 调用 `l3_rpc_notifier.routers_updated_on_host` 发送 router 更新的 RPC 消息

### `def get_dvr_routers_by_subnet_ids(self, context, subnet_ids)`

获取与 subnet 关联的 dvr router

### `def _get_active_l3_agent_routers_sync_data(self, context, host, agent, router_ids)`

1. 若是当前的 router service 支持 ha 模式，则调用 `L3_HA_NAT_db_mixin.get_ha_sync_data_for_host` 获取该 host 上支持 ha 的 router 的详细数据
2. 若是当前的 router service 不支持 ha 模式，则调用 `L3_NAT_with_dvr_db_mixin._get_dvr_sync_data` 获取该 host 上 router 的详细数据

### `def _get_router_ids_for_agent(self, context, agent_db, router_ids)`

1. 调用父类 `L3AgentSchedulerDbMixin` 的 `_get_router_ids_for_agent` 查询数据库 `RouterL3AgentBinding` 获取 router_ids 中与 l3 agent 绑定的 router
2. 若通过数据库查询获取的 router id 与请求的 router id 一致，则直接返回。
3. 若通过数据库查询获取的 router id 与请求的 router id 不一致，且 agent 处于 dvr 模式，则：
 1. 若`router_ids` 为空，则调用 `_get_dvr_router_ids_for_host` 获取该 host 上的提供 dvr 服务的 router，并返回提供 dvr 服务的 router 和与 L3 agent 绑定的 router
 2. 若 `router_ids` 不为空，对于那些未与 l3 agent 绑定的 router：
  1. 调用 `get_subnet_ids_on_router` 返回这些 router 上有关的 subnet
  2. 调用 `_check_dvr_serviceable_ports_on_host` 查询该 host 上是否有属于 subnet_ids 的提供 dvr service 的 port，若是有则认为该 router 也是与该 host 有关的，返回所有与 l3 agent 绑定的 router，并且与 l3 agent 有关的 router。

### `def _get_dvr_router_ids_for_host(self, context, host)`

1. 调用 `_get_dvr_subnet_ids_on_host_query` 获取与该 host 绑定的所有 port 的 subnet
2. 根据上面的 subnet，在查询数据库 `Port` 获取该 host 上的提供 dvr 服务的 router

### `def _get_dvr_subnet_ids_on_host_query(self, context, host)`

通过查询数据库 `IPAllocation`、`Port`、`PortBinding` 数据库，获取与该 host 绑定的所有 port 的 subnet 

## `def subscribe()`

*订阅资源事件*

```
def subscribe():
    registry.subscribe(
        _notify_l3_agent_port_update, resources.PORT, events.AFTER_UPDATE)
    registry.subscribe(
        _notify_l3_agent_new_port, resources.PORT, events.AFTER_CREATE)
    registry.subscribe(
        _notify_port_delete, resources.PORT, events.AFTER_DELETE)
```

## `def _notify_l3_agent_port_update(resource, event, trigger, **kwargs)`

*当 port 资源发生更新时，会调用该方法*

1. 判断新 port 是否需要 dvr 服务
2. 获取 l3 plugin 实例
3. 验证 port 是否是由需要 dvr 服务转向了不需要 dvr 服务
4. 判断 port 绑定的 host 是否发生了变化
5. 若是 port 不再需要 dvr 服务或者 port 绑定的 host 发生了变化，则：
 1. 调用 `get_dvr_routers_to_remove`（这个在 `L3_DVRsch_db_mixin` 和 `L3_DVR_HA_scheduler_db_mixin` 都实现了）删除不再被需要的 router
 2. 若存在需要删除的 router，则调用 `_notify_port_delete` 处理 port 的 `allowed_address_pairs` 相关属性
 3. 调用 `L3_DVRsch_db_mixin._get_floatingip_on_port` 获取该 port 的 floating ip
 4. 若上一步获取的 floating ip 未与即将删除的 router 绑定，则需要调用 `L3AgentNotifyAPI.routers_updated_on_host` 发送 router（与 floating ip 绑定的） 更新的通知
 5. 若 port 新属性不再需要 dvr 服务，则直接返回
6. 若更新后 port 的 host_id 发生了变化（或有了 `migrating_to` 属性）：
  1. 调用 `dvr_handle_new_service_port` 处理该 port 的 floating ip 信息以及 route 信息
  2. 调用 `L3_NAT_with_dvr_db_mixin.update_arp_entry_for_dvr_service_port` 发送 arp 记录更新的 RPC 消息
7. 若 port 的新数据中有 `allowed_address_pairs`属性，且 port 与新的 host 发生了绑定，则：
  1. 若 Port 的 `admin_state_up` 属性是由 False 变为 True，则调用 `_dvr_handle_unbound_allowed_addr_pair_add` 处理 port 的 `allowed_address_pairs` 属性数据
  2. 若 Port 的 `admin_state_up` 属性是由 True 变为 False，则调用 `_dvr_handle_unbound_allowed_addr_pair_del` 处理 port 的 `allowed_address_pairs` 属性数据
  3. 若 Port 的 `admin_state_up` 一直保持 True，则调用 `_dvr_handle_unbound_allowed_addr_pair_add` 处理 port 的 `allowed_address_pairs` 属性数据
8. 若是 port 的 ip 或者 mac 地址发生了变化，则调用 `L3_NAT_with_dvr_db_mixin.update_arp_entry_for_dvr_service_port` 发送 arp 记录更新的 RPC 消息

## `def _notify_port_delete(event, resource, trigger, **kwargs)`

1. 若被删除的 port 存在 `host_id` 和 `allowed_address_pairs` 属性，则调用 `_dvr_handle_unbound_allowed_addr_pair_del` 处理下一与 `allowed_address_pairs` 原 port 相关的信息
2. 调用 `L3_NAT_with_dvr_db_mixin.delete_arp_entry_for_dvr_service_port` 通知 l3 agent 删除相应的 arp table
3. 调用 `L3_DVR_HA_scheduler_db_mixin.L3_DVR_HA_scheduler_db_mixin` 判断哪些不用的 router 可以被删除
4. 若有 router 需要被删除，则调用 `L3AgentNotifyAPI.router_removed_from_agent` 通知 l3 agent 删除 router

## `def _dvr_handle_unbound_allowed_addr_pair_add(plugin, context, port, allowed_address_pair)`

1. 调用 `L3_NAT_with_dvr_db_mixin.update_unbound_allowed_address_pair_port_binding` 处理 port 的 `allowed_address_pairs` 属性
2. 调用 `L3_DVRsch_db_mixin.dvr_handle_new_service_port` 处理该 port 的 floating ip 网关信息以及 route 信息
3. 调用 `L3_NAT_with_dvr_db_mixin.update_arp_entry_for_dvr_service_port` 发送 arp 记录更新的 RPC 消息
 
## `def _dvr_handle_unbound_allowed_addr_pair_del(plugin, context, port, allowed_address_pair)`

1. 调用 `L3_NAT_with_dvr_db_mixin.remove_unbound_allowed_address_pair_port_binding` 处理 port 的 `allowed_address_pairs` 属性
2. 调用 `_get_allowed_address_pair_fixed_ips` 获取 `allowed_address_pairs` 所对应的 subnet 信息
3. 调用 `L3_NAT_with_dvr_db_mixin.delete_arp_entry_for_dvr_service_port` 通知 l3 agent 删除相应的 arp table

## `def _notify_l3_agent_new_port(resource, event, trigger, **kwargs)`

* 若是新 port 需要 dvr 服务：
 1. 调用 `L3_DVRsch_db_mixin.dvr_handle_new_service_port` 处理该 port 的 floating ip 网关信息以及 route 信息
 2. 调用 `L3_NAT_with_dvr_db_mixin.update_arp_entry_for_dvr_service_port` 发送 arp 记录更新的 RPC 消息









