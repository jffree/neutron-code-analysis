# Neutron Router Service 之 router_scheduler

router scheduler driver 在 `L3RouterPlugin` 初始化时被加载，默认的 driver 为 `neutron.scheduler.l3_agent_scheduler.LeastRoutersScheduler`。

*neutron/scheduler/l3_agent_scheduler.py*

**调度：即指将 router 与 l3 agent 进行绑定**

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
3. 调用 `schedule_router` 实现 router 与 l3 agent 的绑定
4. 调用 `list_l3_agents_hosting_router` 获取重新调度后与该 router 绑定的 l3 agent
5. 若调度失败，则引发异常
6. 若调度成功，则调用 `_notify_agents_router_rescheduled` 发送 RPC 通知 host 有 router 进行解绑和绑定操作

### `def _unschedule_router(self, context, router_id, agents_ids)`

调用 `_unbind_router` 实现

### `def _unbind_router(self, context, router_id, agent_id)`

删除数据库 `RouterL3AgentBinding` 关于 router（`router_id`） 和 l3 agent（`agent_id`）的绑定记录

### `def schedule_router(self, context, router, candidates=None)`

调用 router schedule_router driver（`LeastRoutersScheduler`） 的 `schedule` 方法实现

### `def **get_l3_agent_candidates**(self, context, sync_router, l3_agents, ignore_admin_state=False)`

1. 判断该 router 是否是 distributed
2. 调用 `get_configuration_dict` 获取 l3 agent 的 configuration
 1. dvr 模式的 l3 agent 不会绑定 router
 2. distributed router 不会与 legacy 模式的 l3 agent 绑定
 3. `handle_internal_only_routers` 为 True，则意味着该 router 在没有 external gateway 的情况下也可以被 l3 agent 处理
 4. `gateway_external_network_id` 和 `external_network_bridge` 选项设置后，l3 agent 只能处理一个 external network（不过 `external_network_bridge` 选项将在 O 版本中被删除）。若是想要 l3 agent 支持多个 external network 这里选项必须为空。
3. 返回可以绑定该 router 的 l3 agent

### `def get_l3_agent_with_min_routers(self, context, agent_ids)`

根据 agent_ids 获取当前 l3 agent 上绑定 router 数量最少的那一个

### `def _notify_agents_router_rescheduled(self, context, router_id, old_agents, new_agents)`

1. 获取 `AGENT_TYPE_L3` 的 notifier（`L3AgentNotifyAPI` 实例）
2. 调用 `L3AgentNotifyAPI.router_removed_from_agent` 发送 RPC 告知有 router 已经不再与 host（解绑的） 上的 l3 agent 绑定了
3. 调用 `L3AgentNotifyAPI.router_added_to_agent` 发送 RPC 告知有 router 与 host（新绑定的） 上的 l3 agent 绑定了

### `def auto_schedule_routers(self, context, host, router_ids)`

调用 router scheduler driver 的 `auto_schedule_routers` 方法实现（在 `L3RpcCallback.get_router_ids` 中被调用）

### `def add_router_to_l3_agent(self, context, agent_id, router_id)`

1. 调用 `router_supports_scheduling` 判断该 router 是否支持调度，若不支持调度则引发异常
2. 调用 `validate_agent_router_combination` 判断该 router 是否可以与 l3 agent 进行绑定
3. 调用 `check_agent_router_scheduling_needed` 检查该 router 是否已经与该 l3 agent 进行绑定
4. 调用 `create_router_to_agent_binding` 完成 router 与 l3 agent 的绑定
5. 调用 `l3_notifier.router_added_to_agent` 发送通知，告诉 l3 agent 有一个 router 被绑定到其上面了

### `def validate_agent_router_combination(self, context, agent, router)`

判断一个 router 是否可以与 l3 agent 进行绑定

1. 判断该 agent 是否是 l3 agent
2. 判断该 l3 agent 是否是 dvr mode（dvr 模式不支持调度）
3. 不可以将 distributed router 绑定到 legacy 模式上的 l3 agent
4. 判断该 router 是否可以与该 l3 agent 绑定
5. 若无法绑定则引发异常 

### `def check_agent_router_scheduling_needed(self, context, agent, router)`

判断该 router 是否需要与该 l3 agent 进行绑定。

1. 判断该 router 是否已经进行过绑定
2. 判断该 router 是否已经与该 l3 agent 进行绑定
3. ha 类型的 router 则认为可以与 l3 agent 进行绑定

### `def create_router_to_agent_binding(self, context, agent, router)`

将一个 router 与 l3 agent 进行绑定。

1. 对于 ha router，调用 `router_scheduler.create_ha_port_and_bind` 实现绑定
2. 对于其他的 router，调用 `router_scheduler.bind_router` 进行绑定

### `def remove_router_from_l3_agent(self, context, agent_id, router_id)`

1. 调用 `_unbind_router` 删除数据库中 router 与 l3 agent 的绑定记录
2. 若 router 是 ha 类型，则调用 `delete_ha_interfaces_on_host` 删除与该 l3 agent 绑定的 router 上的 ha port
3. 若 router 是 distributed 类型，则：
 1. 调用 `L3_DVRsch_db_mixin.get_subnet_ids_on_router` 获取该 router 上 port 所属的 subnet
 2. 调用 `L3_DVRsch_db_mixin._check_dvr_serviceable_ports_on_host` 查询该 host 上是否有属于 subnet_ids 的提供 dvr service 的 port
4. 获取  notifier（`L3AgentNotifyAPI` 实例）
5. 若存在提供 dvr service 的 port，则调用 `notifier.routers_updated_on_host` 发送 RPC 消息
6. 若不存在提供 dvr service 的 port，则调用 `notifier.router_removed_from_agent` 发送 RPC 消息

### `def list_routers_on_l3_agent(self, context, agent_id)`

查询数据库 `RouterL3AgentBinding` 获取与 agent_id 绑定的所有 router

### `def list_router_ids_on_host(self, context, host, router_ids=None)`

1. 调用 `_get_agent_by_type_and_host` 获取该 host 上的 l3 agent
2. 调用 `_get_router_ids_for_agent` 获取该 l3 agent 绑定的 router 的 id

### `def _get_router_ids_for_agent(self, context, agent, router_ids)`

查询数据库 `RouterL3AgentBinding` 获取 router_ids 中与 l3 agent 绑定的 router

### `def list_active_sync_routers_on_active_l3_agent(self, context, host, router_ids)`

1. 调用 `_get_agent_by_type_and_host` 获取该 host 上的 l3 agent
2. 调用 `_get_router_ids_for_agent` 获取 router_ids 中与该 l3 agent 绑定的 router
3. 调用 `_get_active_l3_agent_routers_sync_data` 获取与 l3 agent 绑定的 routers 中符合要求的详细数据

### `def _get_active_l3_agent_routers_sync_data(self, context, host, agent, router_ids)`

1. 若当前 Router Service 支持 ha extension，则调用 `L3_HA_NAT_db_mixin.get_ha_sync_data_for_host` 获取该 host 上支持 ha 的 router 的详细数据
2. 若当前 Router Service 不支持 ha extension，则调用 `L3_NAT_dbonly_mixin.get_sync_data` 获取该 host 上支持 ha 的 router 的详细数据
3. 调用 `L3_NAT_dbonly_mixin.filter_allocating_and_missing_routers` 过滤掉处于 `ALLOCATING` 状态的 router

### `def get_hosts_to_notify(self, context, router_id)`

1. 调用 `get_l3_agents_hosting_routers` 找出与这些 router_ids 绑定的 l3 agent
2. 获取这些 l3 agent 所在的 host 并返回

### `def get_l3_agents_hosting_routers(self, context, router_ids, admin_state_up=None, active=None)`

通过查询 `RouterL3AgentBinding` 数据库，找出与这些 router_ids 绑定的 l3 agent

## Scheduler Driver: `class LeastRoutersScheduler(L3Scheduler)`

### `def schedule(self, plugin, context, router_id, candidates=None)`

```
    def schedule(self, plugin, context, router_id,
                 candidates=None):
        return self._schedule_router(
            plugin, context, router_id, candidates=candidates)
```

调用 `L3Scheduler._schedule_router` 实现。 

### `def _choose_router_agents_for_ha(self, plugin, context, candidates)`

作用：选取可以绑定 ha router 的 l3 agent

1. 调用 `L3Scheduler._get_num_of_agents_for_ha` 获取准备绑定 ha router 的 l3 agent 的数量
2. 调用 `get_l3_agents_ordered_by_num_routers`（`L3_HA_scheduler_db_mixin` 中实现）根据所有 l3 agent 上已绑定的 router 数量进行排序
3. 取绑定 router 数量少的 l3 agent。

### `def _choose_router_agent(self, plugin, context, candidates)`

调用 `L3AgentSchedulerDbMixin.get_l3_agent_with_min_routers` 在 candidates 中获取绑定 router 数量最少的那个 l3 agent

### `def get_vacant_binding_index(self, context, router_id, is_manual_scheduling=False)`

1. 调用 `L3_HA_NAT_db_mixin.get_number_of_agents_for_scheduling` 获取可为 ha router 绑定的 l3 agent 的数量
2. 查询数据库 `RouterL3AgentBinding` 获取 router(`router_id`) 的 `binding_index` 记录
3. 返回未使用的最小的 `binding_indices`

* `binding_indices` : 对于 ha router 来说，它会与多个 l3 agent 进行绑定，每一个绑定都会有一个 binding_index。这个 `binding_index` 的范围既是 `max_l3_agents_per_router` 或者当前可用 l3 agent 的数量

## `class ChanceScheduler(L3Scheduler)`

*随机为 router 分配 l3 agent 来进行绑定*

```
class ChanceScheduler(L3Scheduler):
    """Randomly allocate an L3 agent for a router."""

    def schedule(self, plugin, context, router_id,
                 candidates=None):
        return self._schedule_router(
            plugin, context, router_id, candidates=candidates)

    def _choose_router_agent(self, plugin, context, candidates):
        return random.choice(candidates)

    def _choose_router_agents_for_ha(self, plugin, context, candidates):
        num_agents = self._get_num_of_agents_for_ha(len(candidates))
        return random.sample(candidates, num_agents)
```

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
6. 对于非 ha router 则调用 `self._choose_router_agent`（`LeastRoutersScheduler` 中实现）获取绑定 router 数量最少的那个 l3 agent
7. 调用 `bind_router` 创建 router 与 l3 agent 的绑定记录

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

### `def auto_schedule_routers(self, plugin, context, host, router_ids)`

作用：为某一 host 上的 l3 agent 自动调度 router 来进行绑定

1. 调用 `AgentDbMixin.get_enabled_agent_on_host` 获取当前 host 上的 l3 agent 实例
2. 调用 `_get_routers_to_schedule` 获取那些待绑的 router
3. 若没有发现待绑定 router，且 router service 支持 ha extension，则调用 `_schedule_ha_routers_to_additional_agent` 查找是否有 ha router 可与 l3 agent 进行绑定，若有，则执行绑定动作。
4. 若发现有待绑定的 router，则调用 `_get_routers_can_schedule` 找到那些未与当前 l3 agent 绑定的 router
5. 调用 `_bind_routers` 将 l3 agent 与这些 router 进行绑定

### `def _get_routers_to_schedule(self, context, plugin, router_ids=None)`

1. 若 router_ids 不为空，则调用 `_filter_unscheduled_routers` 找出 router_ids 中未与 l3 agent 绑定的 router
2. 若 router_ids 为空，则调用 `_get_unscheduled_routers` 所有未与 l3 agent 绑定的 router
3. 从获取待绑定的 router 中找出支持调度的 router 并返回

### `def _filter_unscheduled_routers(self, context, plugin, routers)`

通过调用 `get_l3_agents_hosting_routers` 方法判断该 routers 中有哪些是未与 l3 agent 绑定的

### `def _get_unscheduled_routers(self, context, plugin)`

获取所有 router 中未与 l3 agent 绑定的 router

### `def _schedule_ha_routers_to_additional_agent(self, plugin, context, agent)`

1. 调用 `get_ha_routers_l3_agents_counts` 获取所有的 ha router 及其绑定的 l3 agent 的数量的对应关系
2. 检查所有的 ha router 在绑定 l3 agent 的数量上是否已经达到了最大设定值 `cfg.CONF.max_l3_agents_per_router`
3. 调用 `_get_routers_can_schedule` 可与当前 l3 agent 绑定的 router
4. 调用 `_router_has_binding` 判断 router 是否已经与当前的 l3 agent 绑定。
5. 若 router 未与当前的 l3 agent 绑定，则调用 `create_ha_port_and_bind` 创建 ha port，并将 ha port 和 router 都与 l3 agent 进行绑定

### `def get_ha_routers_l3_agents_counts(self, context, plugin, filters=None)`

```
    def get_ha_routers_l3_agents_counts(self, context, plugin, filters=None):
        """Return a mapping (router, # agents) matching specified filters."""
        return plugin.get_ha_routers_l3_agents_count(context)
```

`get_ha_routers_l3_agents_count` 在 `L3_HA_scheduler_db_mixin` 中实现（获取所有的 ha router 及其绑定的 l3 agent 的数量的对应关系）

### `def _get_routers_can_schedule(self, context, plugin, routers, l3_agent)`

获取可与当前 l3 agent 绑定的 router

### `def _router_has_binding(self, context, router_id, l3_agent_id)`

判断 router 是否已经于当前的 l3 agent 绑定

### `def create_ha_port_and_bind(self, plugin, context, router_id, tenant_id, agent, is_manual_scheduling=False)`

1. 调用 `L3AgentSchedulerDbMixin.get_vacant_binding_index` 获取该 router 最小的还未使用 `binding_index`
2. 调用 `bind_router` 创建 ha router 与 l3 agent 的绑定记录 `RouterL3AgentBinding`
3. 调用 `utils.create_object_with_dependency` 完成 ha port 的创建。
 1. 调用 `L3_HA_NAT_db_mixin.get_ha_network` 判断该租户的 ha network 是否已经创建
 2. 若是 ha network 还未创建，则调用 `L3_HA_NAT_db_mixin._create_ha_network` 创建该租户的 ha network 
 3. 调用 `_add_port_from_net` 完成 ha port 的创建
 4. 若创建 ha port 的过程中发生失败，且查过了最大重试次数，则调用 `L3_HA_NAT_db_mixin._delete_ha_network` 删除上面创建的 ha network。
4. ha port 创建成功后，在对应的 `L3HARouterAgentPortBinding` 记录中增加 l3 agent id 的字段

### `def _add_port_from_net(self, plugin, ctxt, router_id, tenant_id, ha_net)`

```
    def _add_port_from_net(self, plugin, ctxt, router_id, tenant_id, ha_net):
        """small wrapper function to unpack network id from ha_network"""
        return plugin.add_ha_port(ctxt, router_id, ha_net.network.id,
                                  tenant_id)
```

`add_ha_port` 在 `L3_HA_NAT_db_mixin` 中定义。

### `def _bind_routers(self, context, plugin, routers, l3_agent)`

一次将多个 router 绑定到 l3 agent 上

1. 若 router 是 ha router，则调用 `_router_has_binding` 检查该 router 是否已经与这个 l3 agent 进行绑定，若未绑定则调用 `create_ha_port_and_bind` 创建 ha port，并将 router 与 l3 agent 进行绑定
2. 对于非 ha router，则调用 `bind_router` 将 router 与 l3 agent 进行绑定