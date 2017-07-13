# Neutron WSGI 之 dhcp agent scheduler

* extention：*neutron/extensions/dhcpagentscheduler.py*
* WSGI 实现：*neutron/db/agentschedulers_db.py* 中的 `DhcpAgentSchedulerDbMixin`

这个插件使用的 controller 不是 *neutron/api/v2/base.py* 中的 `Controller` 类，而是在 *neutron/extensions/dhcpagentscheduler.py* 中的 `NetworkSchedulerController` 和 `DhcpAgentsHostingNetworkController`


我们先看这个 `NetworkSchedulerController` 和 `DhcpAgentsHostingNetworkController`

## `class NetworkSchedulerController(wsgi.Controller)`

### `def index(self, request, **kwargs)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/agents/58ea7075-d9e6-4070-9e57-bbce22335f2c/dhcp-networks -H 'Content-Type: application/json' -H 'X-Auth-Token: e9581305cf85426aba12345c328a1f8f' | jq
```

1. 获取 core plugin 实例
2. 调用 `policy.enforce` 对 `get_dhcp-networks` 动作进行检查
3. 调用 core plugin 的 `list_networks_on_dhcp_agent` 方法

### `def create(self, request, body, **kwargs)`

1. 获取 core plugin 实例
2. 调用 `policy.enforce` 对 `create_dhcp-networks` 动作进行检查
3. 调用 core plugin 的 `add_network_to_dhcp_agent` 方法
4. 调用 oslo_message 的 Notifier 发送 `dhcp_agent.network.add` 的通知

### `def delete(self, request, id, **kwargs)`

测试方法：

```
curl -s -X DELETE http://172.16.100.106:9696//v2.0/agents/58ea7075-d9e6-4070-9e57-bbce22335f2c/dhcp-networks/534b42f8-f94c-4322-9958-2d1e4e2edd47 -H 'Content-Type: application/json' -H 'X-Auth-Token: e9581305cf85426aba12345c328a1f8f'
```

1. 获取 core plugin 实例
2. 调用 `policy.enforce` 对 `delete_dhcp-networks` 动作进行检查
3. 调用 core plugin 的 `remove_network_from_dhcp_agent` 方法
4. 调用 oslo_message 的 Notifier 发送 `dhcp_agent.network.remove` 的通知

## `class DhcpAgentsHostingNetworkController(wsgi.Controller)`

### `def index(self, request, **kwargs)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/networks/534b42f8-f94c-4322-9958-2d1e4e2edd47/dhcp-agents -H 'Content-Type: application/json' -H 'X-Auth-Token: e9581305cf85426aba12345c328a1f8f' | jq
```

1. 获取 core plugin 实例
2. 调用 `policy.enforce` 对 `get_dhcp-agents` 动作进行检查
3. 调用 core plugin 的 `list_dhcp_agents_hosting_network` 方法

## `class DhcpAgentSchedulerPluginBase(object)`

抽象基类

## `DhcpAgentSchedulerDbMixin`

```
class DhcpAgentSchedulerDbMixin(dhcpagentscheduler                                                                                                                     
                                .DhcpAgentSchedulerPluginBase,
                                AgentSchedulerDbMixin)
```

继承于 `DhcpAgentSchedulerPluginBase`， WSGI 的具体实现

### `def list_active_networks_on_active_dhcp_agent(self, context, host)`

获取与 host 主机上的 dhcp agent 绑定的所有 network

### `def list_networks_on_dhcp_agent(self, context, id)`

1. 查询 `NetworkDhcpAgentBinding`，获取与指定 dhcp agent (`id`) 绑定的 network 的 `id`
2. 调用 `get_networks`方法，根据 network 的 `id` 获取 network 的详细信息。

### `def add_network_to_dhcp_agent(self, context, id, network_id)`

1. 调用 `AgentDbMixin._get_agent` 获取 agents 数据库查询结果
2. 判断该 agent 是否为 dhcp 类型，同时判断该 agent 的 `admin_state_up` 是否为 true
3. 调用 `get_dhcp_agents_hosting_networks` 根据 `network_ids` 获取与之绑定的处于活动状态的 agent
4. 根据刚才获取的 agent 判断该 `id` 是否已经和 `network_id` 绑定过
5. 没有绑定的情况下，增加一条 `NetworkDhcpAgentBinding` 的绑定记录
6. 调用 `agent_notifiers.get(constants.AGENT_TYPE_DHCP)` dhcp agent notifier 发送 RPC 消息 

### `def get_dhcp_agents_hosting_networks(self, context, network_ids, active=None, admin_state_up=None,hosts=None)`

1. 对 `NetworkDhcpAgentBinding` 和 `Agent` 数据库做联合查询，根据 `network_ids`、`admin_state_up` 和 `hosts` 来进行过滤。
2. 调用 `is_eligible_agent` 判断查询结果中的 agent 是否是活动的或者是刚启动的
3. 收集活动的和刚启动的 agent 返回

### `def is_eligible_agent(self, context, active, agent)`

1. 调用 `AgentSchedulerDbMixin.is_eligible_agent` 判断 agent 是否是活动的
2. 调用 `agent_starting_up` 判断 agent 是否处于正在启动的时间段里
3. 对于活动的或者正在启动的 agent 返回 True

### `def remove_network_from_dhcp_agent(self, context, id, network_id,                                       notify=True)`

1. 根据 `id` 和 `network_id` 查询 `NetworkDhcpAgentBinding` 数据库
2. 调用 `utils.get_dhcp_agent_device_id` 获得 dhcp 在该 network 上的专用 device_id
3. 根据 device_id 获取 port
4. 更改 port 的 `device_id` 属性为 `n_const.DEVICE_ID_RESERVED_DHCP_PORT`（对每个 dhcp agent 和 每个 network 来说，会仅有一个 port，**专属？？**）
5. 删除 `NetworkDhcpAgentBinding` 中的记录
6. 调用 `self.agent_notifiers.get(constants.AGENT_TYPE_DHCP)` 发送通知

### `def list_dhcp_agents_hosting_network(self, context, network_id)`

1. 调用 `get_dhcp_agents_hosting_networks` 获取与这个 network 绑定的 dhcp agent
2. 获取绑定的 dhcp agent 的 id
3. 调用 `get_agents` 获取详细信息

### `def start_periodic_dhcp_agent_status_check(self)`

使用 `remove_networks_from_down_agents` 方法对 dhcp agent 的状态进行间隔循环检查。这个方法已经被弃用，被 `def add_periodic_dhcp_agent_status_check(self)` 方法取代。

### `def add_periodic_dhcp_agent_status_check(self)`

使用 `remove_networks_from_down_agents` 方法对 dhcp agent 的状态进行间隔循环检查。

### `def remove_networks_from_down_agents(self)`

1. 从数据库 `NetworkDhcpAgentBinding` 和 `Agent` 中获取那些已经死亡的 agent
2. 调用 `_filter_bindings` 过滤掉那些处于启动状态的 agent
3. 调用 `get_agents_db` 获取处于活动状态和启动状态的该类型的 agent
4. 调用 `remove_network_from_dhcp_agent` 从已死亡的 dhcp agent 中去除 networks 的绑定
5. 在配置了 `if cfg.CONF.network_auto_schedule` 的情况下，调用 `_schedule_network` 进行资源的重新绑定
 
### `def _schedule_network(self, context, network_id, dhcp_notifier)`

1. 调用 `get_network` 获取 network 资源
2. 调用 `schedule_network` 进行资源的重新配置
3. 调用 `dhcp_notifier` 发送通知

### `def schedule_network(self, context, created_network)`

```
    def schedule_network(self, context, created_network):
        if self.network_scheduler:
            return self.network_scheduler.schedule(
                self, context, created_network)
```

讲到这里，我们又要去 ml2 的 `Ml2Plugin._setup_dhcp` 瞅一眼了：

```
    def _setup_dhcp(self):
        """Initialize components to support DHCP."""
        self.network_scheduler = importutils.import_object(
            cfg.CONF.network_scheduler_driver
        )
        self.add_periodic_dhcp_agent_status_check()
```

在 */etc/neutron/neutron.conf* 中，我们可以找到这个调度驱动的选项：

```
network_scheduler_driver = neutron.scheduler.dhcp_agent_scheduler.WeightScheduler
```

剩下的请参考：**Neutron Dhcp Scheduler**

### `def _filter_bindings(self, context, bindings)`

从 bindings 中过滤掉那些处于启动期的 agent（处于启动期并不算死亡）

### `def is_eligible_agent(self, context, active, agent)`

判断一个  agent 是否活着或处于启动时期

### `def agent_starting_up(self, context, agent)`

判断 agent 是否处于启动时期

### `def auto_schedule_networks(self, context, host)`

调用 `self.network_scheduler.auto_schedule_networks` 方法实现



## `class AgentStatusCheckWorker(neutron_worker.NeutronWorker)`

一个 neutron 的 worker，会在一个绿色线程中启动

这个 worker 的作用是：定期循环调用检查函数来检查 agent 的状态

* **check_func** : 检查 agent 状态的方法
* **loop** : 定期循环检查的实现（[`loopingcall.FixedIntervalLoopingCall` 固定间隔循环呼叫](https://docs.openstack.org/developer/oslo.service/api/loopingcall.html#oslo_service.loopingcall.FixedIntervalLoopingCall)）
* **_interval** : 间隔时间
* **_initial_delay** : 开始循环之前的延迟时间

## `class AgentSchedulerDbMixin(agents_db.AgentDbMixin)`

这是一个基础类，实现一些 agent 的封装功能

`agents_db.AgentDbMixin` 这个我在 **Neutron WSGI 之 agent** 中讲过

### `def agent_dead_limit_seconds(self)`

返回一个秒数，这个秒数用来判断代理是否已经死亡。

若是心跳检测时间距当前时间超过这个秒数，则认为代理已经彻底死亡。

### `def is_eligible_agent(active, agent)`

判断 agent 是否还在运行

### `def update_agent(self, context, id, agent)`

更新 agent 数据，调用 `self.agent_notifiers.get(original_agent['agent_type'])` 发送 agent 更新的消息

### `def add_agent_status_check_worker(self, function)`

增加 agent 的状态检查 worker

### `def add_agent_status_check(self, function)`

该方法已经被 `add_agent_status_check_worker` 取代

### `def wait_down_agents(self, agent_type, agent_dead_limit)`

可能有的 agent 在判断时间内未能进行心跳检测，该方法就是给这样的 agent 一定的缓冲时间去进行心跳检测。

### `def get_cutoff_time(self, agent_dead_limit)`

用于查看 agent 是否已经死亡达到最长允许时间

### `reschedule_resources_from_down_agents`

```
def reschedule_resources_from_down_agents(self, agent_type,
                                              get_down_bindings,
                                              agent_id_attr,
                                              resource_id_attr,
                                              resource_name,
                                              reschedule_resource,
                                              rescheduling_failed)
```

对于已经死掉的 agent 上的资源进行重新调度，这个方法在 l3 agent 上用到，到时候我们再讲。