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

填充 network 的 `provider:network_type` 和 `provider:physical_network` 属性

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

1. 调用 `get_ha_router_port_bindings` 获取某台机器 host 上 router_ids 上绑定的 ha port 
2. 放弃那些没有 ha port 的 router
3. 为所有带有 ha port 的 router 增加 `_ha_interface` 和 `_ha_state` 属性
4. 调用 `ExtraRoute_dbonly_mixin._populate_mtu_and_subnets_for_ports` 为所有的 ha port 增加 subnet 数据和 mtu
5. 若 agent 为 dvr 模式，则返回所有的带有 ha port 的 router 数据
6. 返回带有 `ha` 属性或者带有 `_ha_interface` 属性的 router 数据

### `def _check_router_agent_ha_binding(context, router_id, agent_id)`

查询数据库 `L3HARouterAgentPortBinding` 判断该 router 是否是在 agent 上提供 ha 服务















