# Neutron router service 之 `L3_DVR_HA_scheduler_db_mixin`

*neutron/db/l3_dvr_ha_scheduler.py*

**作用：**综合了在同时拥有 ha 和 dvr 功能的情况下，l3 agent scheduler 的实现

## `class L3_DVR_HA_scheduler_db_mixin(l3agent_dvr_sch_db.L3_DVRsch_db_mixin, l3_ha_sch_db.L3_HA_scheduler_db_mixin)`

### `def get_dvr_routers_to_remove(self, context, port_id)`

当一个需要 dvr 服务的 port 被删除时，我们要考虑是否需要将该 host 上提供 dvr 服务的 router 进行删除

1. 调用 `L3_DVRsch_db_mixin.get_dvr_routers_to_remove` 只处理在 dvr 服务情况下有哪些 router 需要删除
2. 调用 `_check_router_agent_ha_binding` 判断该 router 是否是在提供 ha 服务，若该 router 不提供 ha 服务，则可以删除，若是提供 ha 服务，则不可以删除


