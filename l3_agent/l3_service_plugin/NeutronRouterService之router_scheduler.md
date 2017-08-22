# Neutron Router Service 之 router_scheduler

router scheduler driver 在 `L3RouterPlugin` 初始化时被加载，默认的 driver 为 `neutron.scheduler.l3_agent_scheduler.LeastRoutersScheduler`。

*neutron/scheduler/l3_agent_scheduler.py*

## extension

*neutron/extensions/l3agentscheduler.py*

## 数据库 RouterL3AgentBinding

```
class RouterL3AgentBinding(model_base.BASEV2):
    """Represents binding between neutron routers and L3 agents."""

    __table_args__ = (
        sa.UniqueConstraint(
            'router_id', 'binding_index',
            name='uniq_router_l3_agent_binding0router_id0binding_index0'),
        model_base.BASEV2.__table_args__
    )

    router_id = sa.Column(sa.String(36),
                          sa.ForeignKey("routers.id", ondelete='CASCADE'),
                          primary_key=True)
    l3_agent = orm.relation(agents_db.Agent)
    l3_agent_id = sa.Column(sa.String(36),
                            sa.ForeignKey("agents.id", ondelete='CASCADE'),
                            primary_key=True)
    binding_index = sa.Column(sa.Integer, nullable=False,
                              server_default=str(LOWEST_BINDING_INDEX))	
```

记录 router 与 l3 agent 的绑定情况

## WSGI 业务实现 `class L3AgentSchedulerDbMixin(l3agentscheduler.L3AgentSchedulerPluginBase, agentschedulers_db.AgentSchedulerDbMixin)`

### `def list_l3_agents_hosting_router(self, context, router_id)`

调用 `_get_l3_bindings_hosting_routers` 获取与 router 绑定的 l3 agent
调用 `_make_agent_dict` 返回与这些 agent 的描述

### `def _get_l3_bindings_hosting_routers(self, context, router_ids)`

查询数据库 `RouterL3AgentBinding`，获取与 router_ids 代表的 router 绑定的 l3 agent。

### `def get_l3_agents(self, context, active=None, filters=None)`

获取符合条件的 l3 agent

### `def add_periodic_l3_agent_status_check(self)`

若配置中 `allow_automatic_l3agent_failover` 为 True，则会在 l3 agent 挂掉时自动重新调度其上面的 router。

若是上述配置为 True，则会调用 `add_agent_status_check_worker`，创建一个 worker（该 worker 运行 `reschedule_routers_from_down_agents` 方法） 来定期检查 l3 agent 的状态，并在其挂掉时，重新调度 router。

### `def reschedule_routers_from_down_agents(self)` 

该方法通过调用 `AgentSchedulerDbMixin.reschedule_resources_from_down_agents` 来实现。

1. 调用 `get_down_router_bindings` 获取绑定有 router 但是挂掉的 l3 agent
2. 调用 `reschedule_router` 对 router 进行重新的调度

### `def get_down_router_bindings(self, context, agent_dead_limit)`

通过联合查询 `RouterL3AgentBinding` 和 `Agent` 数据库，获取绑定有 router 但是挂掉的 l3 agent

### `def reschedule_router(self, context, router_id, candidates=None)`

1. 调用 `list_l3_agents_hosting_router` 获取当前绑定有 router（`router_id`） 的 l3 agent
2. 调用 `_unschedule_router` 删除 router 与 l3 agent 的绑定记录
3. 调用 `schedule_router`


### `def _unschedule_router(self, context, router_id, agents_ids)`

调用 `_unbind_router` 实现

### `def _unbind_router(self, context, router_id, agent_id)`

删除数据库 `RouterL3AgentBinding` 关于 router（`router_id`） 和 l3 agent（`agent_id`）的绑定记录

### `def schedule_router(self, context, router, candidates=None)`

调用 router schedule_router driver（`LeastRoutersScheduler`） 的 `schedule` 方法实现

### `def get_l3_agent_candidates(self, context, sync_router, l3_agents, ignore_admin_state=False)`

1. 判断该 router 是否是 distributed
2. 调用 `get_configuration_dict` 获取 l3 agent 的 configuration
 1. dvr 模式的 l3 agent 不会绑定 router
 2. distributed router 不会与 legacy 模式的 l3 agent 绑定
 3. `handle_internal_only_routers` 为 True，则意味着该 router 在没有 external gateway 的情况下也可以被 l3 agent 处理
 4. `gateway_external_network_id` 和 `external_network_bridge` 选项设置后，l3 agent 只能处理一个 external network（不过 `external_network_bridge` 选项将在 O 版本中被删除）。若是想要 l3 agent 支持多个 external network 这里选项必须为空。
3. 返回可以绑定该 router 的 l3 agent


## Scheduler Driver: `class LeastRoutersScheduler(L3Scheduler)`

### `def schedule(self, plugin, context, router_id, candidates=None)`

```
    def schedule(self, plugin, context, router_id,
                 candidates=None):
        return self._schedule_router(
            plugin, context, router_id, candidates=candidates)
```

### `def _choose_router_agents_for_ha(self, plugin, context, candidates)`

作用：选取可以绑定 ha router 的 l3 agent

1. 调用 `L3Scheduler._get_num_of_agents_for_ha` 获取准备绑定 ha router 的 l3 agent 的数量
2. 调用 `get_l3_agents_ordered_by_num_routers`（`L3_HA_scheduler_db_mixin` 中实现）根据所有 l3 agent 上已绑定的 router 数量进行排序
3. 取绑定 router 数量少的 l3 agent。


调用 `L3Scheduler._schedule_router` 实现。 

## `class ChanceScheduler(L3Scheduler)`






## `class L3Scheduler(object)`

```
    def __init__(self):
        self.min_ha_agents = cfg.CONF.min_l3_agents_per_router
        self.max_ha_agents = cfg.CONF.max_l3_agents_per_router
```

* `min_l3_agents_per_router`：默认为2
* `max_l3_agents_per_router`：默认为3

### `def _schedule_router(self, plugin, context, router_id, candidates=None)`

1. 调用 l3 agent 的 `router_supports_scheduling` 判断该 router 是否支持调度
 * 目前的 router 共有4中类型：dvr、dvrha、ha、single_node（这四种类型全部支持调度）
2. 调用 `plugin.get_router` 获取该 router 的数据
3. 若未知名 candidates（候选的 l3 agent），则调用 `_get_candidates` 获取可以与 router 绑定的 l3 agent
4. 若是没有可与 router 绑定的 l3 agent 则直接退出。
5. 若是 router 有 ha 属性，则调用 `self._bind_ha_router` 将该 ha router 绑定到 l3 agent 上
6. 对于非 ha router 则调用 `self._choose_router_agent`















### `def _get_candidates(self, plugin, context, sync_router)`

1. 调用 `l3.get_l3_agents_hosting_routers` 判断当前的 router 是否已经与某一 l3 agent 绑定，若是已经绑定则直接退出
2. 调用 `plugin.get_l3_agents` 获取所有 active 的 l3 agent
3. 调用 `plugin.get_l3_agent_candidates` 获取合适的可与 router 绑定的 l3 agent

### `def _bind_ha_router(self, plugin, context, router_id, candidates)`

1. 调用 `self._enough_candidates_for_ha` 是否有足够数量的 l3 agent 来部署 router ha
2. 调用 `self._choose_router_agents_for_ha`（`LeastRoutersScheduler` 中实现）选取合适的 l3 agent
3. 调用 `self._bind_ha_router_to_agents` 将 ha router 绑定到 l3 agent 上（创建 `RouterL3AgentBinding` 记录，更新 `L3HARouterAgentPortBinding` 记录）。

### `def _enough_candidates_for_ha(self, candidates)`

判断当前可绑定 router 的 l3 agent 是不是小于配置中设定的最小数量

### `def _get_num_of_agents_for_ha(self, candidates_count)`

对于 ha router 来说，判断可以绑定几个 l3 agent

### `def _bind_ha_router_to_agents(self, plugin, context, router_id, chosen_agents)`

1. 调用 `get_ha_router_port_bindings`（`L3_HA_NAT_db_mixin`实现） 获取该 router 上的 ha port 的数据库 `L3HARouterAgentPortBinding` 记录
2. 调用 `bind_router` 创建 `RouterL3AgentBinding` 数据库记录
3. 更新该 `L3HARouterAgentPortBinding` 记录中关于 `l3_agent_id` 的字段


### `def bind_router(self, context, router_id, chosen_agent, binding_index=l3_agentschedulers_db.LOWEST_BINDING_INDEX)`

创建一个 `RouterL3AgentBinding` 数据库记录，用来记录 router 与 l3 agent 的绑定记录
