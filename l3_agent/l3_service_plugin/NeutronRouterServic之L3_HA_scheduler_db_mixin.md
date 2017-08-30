# Neutron Router Service 之 L3_HA_scheduler_db_mixin

*neutron/db/l3_hascheduler_db.py*

## `class L3_HA_scheduler_db_mixin(l3_sch_db.AZL3AgentSchedulerDbMixin)`

### `def get_ha_routers_l3_agents_count(self, context)`

* 获取所有的 ha router 及其绑定的 l3 agent 的数量的对应关系

### `def get_l3_agents_ordered_by_num_routers(self, context, agent_ids)`

根据 agent 上绑定 router 的数量对 agent_ids 排序

### `def _get_agents_dict_for_router(self, agents_and_states)`

1. 调用 `_make_agent_dict` 返回 agent 的易读数据
2. 为 agent 数据增加 `ha_state` 属性

### `def list_l3_agents_hosting_router(self, context, router_id)`

1. 若为 ha router，则调用 `L3_HA_NAT_db_mixin.get_l3_bindings_hosting_router_with_ha_states` 获取 router 绑定的数据
2. 若不是 ha router，则调用 `_get_l3_bindings_hosting_routers` 获取 router 的绑定数据
3. 调用 `_get_agents_dict_for_router` 返回 agent 的数据。

## `def subscribe()`

```
def subscribe():
    registry.subscribe(
        _notify_l3_agent_ha_port_update, resources.PORT, events.AFTER_UPDATE)
```

## `def _notify_l3_agent_ha_port_update(resource, event, trigger, **kwargs)`

若 port 为 ha 类型，且 port 的状态变为 active，则调用 `l3_rpc_notifier.routers_updated_on_host` 更新其 host 上的路由信息