# Neutron router service 之 `L3_DVR_HA_scheduler_db_mixin`

*neutron/db/l3_dvr_ha_scheduler.py*

**作用：**综合了在同时拥有 ha 和 dvr 功能的情况下，l3 agent scheduler 的实现

## `class L3_DVR_HA_scheduler_db_mixin(l3agent_dvr_sch_db.L3_DVRsch_db_mixin, l3_ha_sch_db.L3_HA_scheduler_db_mixin)`

### `def L3_DVR_HA_scheduler_db_mixin(self, context, port_id)`

*Process the router information which was returned to make sure we don't delete routers which have dvrhs snat bindings.*

1. 调用 `L3_DVRsch_db_mixin.get_dvr_routers_to_remove` 找到需要删除的 dvr router
2. 调用 `_check_router_agent_ha_binding` 判断该 router 是否作为 ha router 与该 agent 绑定的
3. 若该 router 是 ha router，并与 agent 绑定，则不能删除该 router 的绑定