# Neutron router service 之 `L3_DVR_HA_scheduler_db_mixin`

*neutron/db/l3_dvr_ha_scheduler.py*

## `class L3_DVR_HA_scheduler_db_mixin(l3agent_dvr_sch_db.L3_DVRsch_db_mixin, l3_ha_sch_db.L3_HA_scheduler_db_mixin)`

### `def get_dvr_routers_to_remove(self, context, port_id)`

## `class L3_DVRsch_db_mixin(l3agent_sch_db.L3AgentSchedulerDbMixin)`

## `class L3_HA_scheduler_db_mixin(l3_sch_db.AZL3AgentSchedulerDbMixin)`

### `def list_l3_agents_hosting_router(self, context, router_id)`

1. 调用 `_get_router` 方法（在 `L3_NAT_dbonly_mixin` 中实现）获取 Router 数据库中的记录
2. 若是该 router 支持 ha 属性，则调用 `get_l3_bindings_hosting_router_with_ha_states` 方法（在 `L3HARouterNetwork` 中实现）
3. 若是该 router 不支持 ha 属性，则调用 `_get_l3_bindings_hosting_routers` 方法获取与该 router 绑定的所有 l3 agent 


## `class AZL3AgentSchedulerDbMixin(L3AgentSchedulerDbMixin, router_az.RouterAvailabilityZonePluginBase)`

## `class L3AgentSchedulerDbMixin(l3agentscheduler.L3AgentSchedulerPluginBase, agentschedulers_db.AgentSchedulerDbMixin)`


### `def _get_l3_bindings_hosting_routers(self, context, router_ids)`

查询 `RouterL3AgentBinding` 数据库，获取与 routers_ids 绑定的数据库记录

### `def get_l3_agent_candidates(self, context, sync_router, l3_agents,ignore_admin_state=False)`

1. 调用 `get_configuration_dict` 获取 l3 agent 的 configuration
2. l3 agent 为 dvr 模式时该 agent 不支持绑定
3. 已经绑定过 router 的 l3 agent 不再操作



## `class AgentSchedulerDbMixin(agents_db.AgentDbMixin)`

*这一个，我在已经分析过了*

## `class L3AgentSchedulerPluginBase(object)`

*neutron/extensions/l3agentscheduler.py*

抽象基类，为实现 l3 agent scheduler REST API 的框架

## `class RouterAvailabilityZonePluginBase(object)`

抽象基类

*neutron/extensions/router_availiability_zone.py*

为 router 增加 `availability_zones` 和 `availability_zone_hints` 属性的 extension
















