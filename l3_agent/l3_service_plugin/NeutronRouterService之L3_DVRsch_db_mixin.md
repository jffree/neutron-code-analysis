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



