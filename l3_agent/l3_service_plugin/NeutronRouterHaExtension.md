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

### `def _verify_configuration(self)`

验证 `l3_ha_net_cidr` 的配置是否正确

### `def _check_num_agents_per_router(self)`

检查 `max_l3_agents_per_router` 和 `min_l3_agents_per_router` 配置是否正确

### `def get_ha_network(self, context, tenant_id)`

通过查询数据库 `L3HARouterNetwork` 判断该租户的 ha network 是否已经创建

### `def _create_ha_network(self, context, tenant_id)`

1. 调用 `_add_ha_network_settings` 完善 ha network 的属性
2. 调用 `common_db_mixin.safe_creation` 完成 ha network 的创建：
 1. 调用 `core_plugin.create_network` 完成 ha network 的创建
 2. 调用 `_create_ha_network_tenant_binding` 创建一个 `L3HARouterNetwork` 数据库记录，用来记录 ha network id 与 tenant_id 的绑定
 3. 若是数据库记录创建失败，则调用 `_core_plugin.delete_network` 删除刚刚创建的 ha network
3. 创建 ha network 成功后，则调用 `_create_ha_subnet` 完成 ha network subnet 的创建

### `def _add_ha_network_settings(self, network)`

填充 network 的 `provider:network_type`（`l3_ha_network_type`） 和 `provider:physical_network`（`l3_ha_network_physical_name`） 属性

### `def _create_ha_network_tenant_binding(self, context, tenant_id, network_id)`

创建一个 `L3HARouterNetwork` 数据库记录，用来记录 ha network id 与 tenant_id 的绑定

### `def _create_ha_subnet(self, context, network_id, tenant_id)`

通过调用 `core_plugin.create_subnet` 来完成 ha network subnet 的创建

### `def add_ha_port(self, context, router_id, network_id, tenant_id)`

* 通过 `common_db_mixin.safe_creation` 的调用完成 ha router port 的创建：
 1. 调用 `core_plugin.create_port` 创建一个与 router 绑定的 ha port
 2. 调用 `_create_ha_port_binding` 创建 `RouterPort` 和 `L3HARouterAgentPortBinding` 的数据库记录
 3. 若数据库创建失败，则调用 `core_plugin.delete_port` 删除刚才创建的 ha port

### `def _create_ha_port_binding(self, context, router_id, port_id)`

1. 创建一个 `RouterPort` 的数据库记录
2. 创建一个 `L3HARouterAgentPortBinding` 的数据库记录（**注意：**此时这个数据库记录中还没有 l3 agent id，l3 agent id 是完成绑定之后添加进去的）。

### `def _delete_ha_network(self, context, net)`

调用 `core_plugin.delete_network` 删除 net 所代表的 ha network

### `def get_ha_router_port_bindings(self, context, router_ids, host=None)`

查询数据库 `L3HARouterAgentPortBinding` 获取某台机器 host 上 router_ids 上绑定的 ha port 

### `def get_number_of_agents_for_scheduling(self, context)`

1. 调用 `get_l3_agents` 获取 legacy 和 dvr_sant 类型 agent 的数量。
2. 可调度的 l3 agent 数量与 `cfg.CONF.min_l3_agents_per_router` 和 `cfg.CONF.max_l3_agents_per_router` 进行对比，获取可为 ha router 进行调度的 l3 agent 的数量

### `def delete_ha_interfaces_on_host(self, context, router_id, host)`

1. 调用 `get_ha_router_port_bindings` 获取某台机器 host 上 router_ids 上绑定的 ha port 
2. 调用 `core_plugin.delete_port` 删除这个 ha port

### `def get_ha_sync_data_for_host(self, context, host, agent, router_ids=None, active=None)`

1. 对于 dvr 模式的 l3 agent，调用 `L3_NAT_with_dvr_db_mixin._get_dvr_sync_data` 获取 router 的详细信息
2. 对于不支持 dvr 模式的 l3 agent，调用 `L3_NAT_dbonly_mixin.get_sync_data` 获取 router 的详细信息
3. 调用 `_process_sync_ha_data` 处理包含 ha port 的 router，并返回其数据

### `def _process_sync_ha_data(self, context, routers, host, agent_mode)`

1. 调用 `get_ha_router_port_bindings` 获取某台机器 host 上 ha router 的绑定记录
2. 放弃那些没有 ha port 的 router
3. 为所有带有 ha port 的 router 增加 `_ha_interface` 和 `_ha_state` 属性
4. 调用 `ExtraRoute_dbonly_mixin._populate_mtu_and_subnets_for_ports` 为所有的 ha port 增加 subnet 数据和 mtu
5. 若 agent 为 dvr 模式，则返回所有的带有 ha port 的 router 数据
6. 返回带有 `ha` 属性或者带有 `_ha_interface` 属性的 router 数据

### `def _check_router_agent_ha_binding(context, router_id, agent_id)`

查询数据库 `L3HARouterAgentPortBinding` 判断该 router 是否是在 agent 上提供 ha 服务

### `def get_l3_bindings_hosting_router_with_ha_states(self, context, router_id)`

1. 调用 `_get_bindings_and_update_router_state_for_dead_agents` 获取 router 的绑定数据
2. 返回绑定数据中存在 l3 agent 的绑定记录

### `def _get_bindings_and_update_router_state_for_dead_agents(self, context, router_id)`

1. 调用 `get_ha_router_port_bindings` 获取 ha router 的绑定记录
2. 过滤出绑定状态为 active 的绑定
3. 对于处于 active 状态的绑定来说，需要查看其绑定的 l3 agent 是否处于激活状态。若是有的 l3 agent 处于未激活状态，则调用 `update_routers_states` 则更新 router 及 port 的数据
4. 若存在不活动的 l3 agent，则调用 `get_ha_router_port_bindings` 重新获取绑定数据后返回
5. 若不存在不活动的 l3 agent，则直接返回最初获取的绑定数据

### `def update_routers_states(self, context, states, host)`

1. 调用 `get_ha_router_port_bindings` 获取 ha router 的绑定记录
2. 调用 `_set_router_states` 更新这些 router 绑定记录的状态为 state
3. 调用 `_update_router_port_bindings` 判断是否有 router 更新为 active 状态，则将该 router 上的 ha port 和 snat Port 与该 host 绑定

### `def _set_router_states(cls, context, bindings, states)`

更新数据库 `L3HARouterAgentPortBinding` 中 bindings 记录中的状态信息为 states

### `def _update_router_port_bindings(self, context, states, host)`

判断是否有 router 更新为 active 状态，则将该 router 上的 ha port 和 snat Port 与该 host 绑定

### `def create_router(self, context, router)`

1. 调用 `L3_NAT_db_mixin.create_router` 完成 router 的创建
2. 若准备创建的 router 是 ha router，则：
 1. 调用 `_get_router` 获取 router 数据
 2. 调用 `_create_ha_interfaces_and_ensure_network` 完成 ha network 和 ha port 的创建
 3. 调用 `_set_vr_id` 为该 ha router 分配一个 VRID
 4. 调用 `schedule_router` 完成该 ha router 的调度
 5. 调用 `_update_router_db` 更新该 router status 为 active
 6. 调用 `_notify_ha_interfaces_updated` 发送 router 更新的消息
 7. 这个过程中若发生异常，则调用 `delete_router` 删除刚才创建的 ha router

### `def _create_ha_interfaces_and_ensure_network(self, context, router_db)`

1. 调用 `get_ha_network` 判断该租户的 ha network 是否已经创建
2. 若该租户的 ha network 不存在，则调用 `_create_ha_network` 创建一个 ha network
3. 调用 `_create_ha_interfaces` 完成 ha router port 的创建
4. 若 ha router port 创建失败，则调用 `_delete_ha_network` 删除刚才创建的 ha network 

### `def _create_ha_interfaces(self, context, router, ha_network)`

1. 调用 `get_number_of_agents_for_scheduling` 获取可创建 ha router 的 agent 的数量
2. 调用 `add_ha_port` 完成 ha port 的创建

### `def _set_vr_id(self, context, router, ha_network)`

调用 `_allocate_vr_id` 为该 ha router 分配一个 VRID

### `def _allocate_vr_id(self, context, network_id, router_id)`

1. 调用 `_get_allocated_vr_id` 获取该 ha network 上分配的 VRID
2. 获取可用的 VRID
3. 创建一个 `L3HARouterVRIdAllocation` 的数据库记录

### `def _get_allocated_vr_id(self, context, network_id)`

查询数据库 `L3HARouterVRIdAllocation` 返回该 ha network 上分配的 VRID（VRRP路由器的唯一标识）

### `def _notify_ha_interfaces_updated(self, context, router_id, schedule_routers=True)`

调用 `l3_rpc_notifier.routers_updated` 发送 router 更新的消息

### `def _delete_vr_id_allocation(self, context, ha_network, vr_id)`

删除数据库 `L3HARouterVRIdAllocation` 中的一个记录

### `def _delete_ha_interfaces(self, context, router_id)`

1. 调用 `_core_plugin.get_ports` 获取所有的 ha port 记录
2. 调用 `_core_plugin.delete_port` 删除所有的 ha port

### `def _is_ha(cls, router)`

判断该 router 是否是 ha router

### `def _get_device_owner(self, context, router=None)`

1. 若该 router 是 ha router，则返回 `ha_router_replicated_interface`
2. 否则则调用 `L3_NAT_with_dvr_db_mixin._get_device_owner` 获取结果

### `def _process_extra_attr_router_create(self, context, router_db, router_res)`

1. 为 router 增加 ha 属性
2. 调用 `ExtraAttributesMixin._process_extra_attr_router_create` 完成后续的操作

### `def _update_router_db(self, context, router_id, data)`

1. 调用 `_get_router` 获取原 router 数据
2. 若是从非 distributed 和非 ha 模式升级到 distributed 和 ha 是无法实现的
3. 若是从非 distributed 和 ha 模式升级到 distributed 模式是无法实现的
4. 若是从 distributed 和非 ha 模式升级到 ha 模式是无法实现的
5. 若是从 distributed 和 ha 模式升级到非 distributed 模式是无法实现的
6. 若是升级前与升级后的 ha status 发生了变化，则：
 1. 若是 router 的 `admin_state_up` 为 True 则会引发异常
 2. 若 router 的 `admin_state_up` 为 False，则更 router 的 status 为：ALLOCATING
7. 调用 `L3_NAT_with_dvr_db_mixin._update_router_db` 完成 router 的更新
8. 若是 ha 的状态发生了变化，则：
 1. 获取该租户的 ha network
 2. 若是更新后不再需要 ha，则调用 `_delete_vr_id_allocation` 删除 VRID
 3. 调用 `_unbind_ha_router` 解除 ha router 与之前 l3 agent 的绑定
 4. 若是该 router 由非 ha 状态更新至支持 ha，则调用 `_create_ha_interfaces_and_ensure_network` 创建 ha 的接口和网络，并调用 `_set_vr_id` 分配 VRID
 5. 若是该 router 由 ha 状态更新至不支持 ha，则：
  1. 调用 `_delete_ha_interfaces` 删除 ha 端口
  2. 调用 `safe_delete_ha_network` 尝试删除 ha network
  3. 调用 `L3_NAT_db_mixin._migrate_router_ports` 更新 router 的 device owner
  4. 
 6. 调用 `schedule_router` 重新调度 router
 7. 调用 `L3_NAT_with_dvr_db_mixin._update_router_db` 完成 router 的状态更新（active）
 8. 调用 `_notify_ha_interfaces_updated` 发送 router 更新的消息

### `def _unbind_ha_router(self, context, router_id)`

1. 调用 `get_l3_agents_hosting_routers` 查找到拥有该 router 的所有 l3 agent
2. 调用 `remove_router_from_l3_agent` 在 l3 agent 上接触与这些 router 的绑定

### `def safe_delete_ha_network(self, context, ha_network, tenant_id)`

调用 `_delete_ha_network` 尝试删除 network 并处理异常

### `def delete_router(self, context, id)`

1. 调用 `_get_router` 获取 router 数据
2. 调用 `L3_NAT_db_mixin.delete_router` 删除 router
3. 若该 router 支持 ha 服务，则：
 1. 调用 `get_ha_network` 获取 ha 网络
 2. 调用 `_delete_vr_id_allocation` 删除 VRID
 3. 调用 `safe_delete_ha_network` 尝试阐述 ha network

### `def get_active_host_for_ha_router(self, context, router_id)`

1. 调用 `get_l3_bindings_hosting_router_with_ha_states` 获取 router 的绑定数据
2. 获取 router 为 active 的 host

## `def is_ha_router(router)`

判断一个 router 是否提供 ha 服务

## `def is_ha_router_port(device_owner, router_id)`

通过 port 的 device_owner 和 router 的 id，判断该 port 是否是 ha port