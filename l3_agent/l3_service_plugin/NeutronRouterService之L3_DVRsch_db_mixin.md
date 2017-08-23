# Neutron Router Service 之 L3_DVRsch_db_mixin

*neutron/db/l3_dvrscheduler_db.py*

## `class L3_DVRsch_db_mixin(l3agent_sch_db.L3AgentSchedulerDbMixin)`

### `def get_subnet_ids_on_router(self, context, router_id)`

1. 调用 `core_plugin.get_ports` 获取该 router 上的 port
2. 获取这些 port 上所属的 subnet

### `def _check_dvr_serviceable_ports_on_host(self, context, host, subnet_ids)`

通过查询 `PortBinding`、`IPAllocation`、`Port` 数据库，查询该 host 上是否有属于 subnet_ids 的提供 dvr service 的 port
若有，则返回 True，没有则返回 False

