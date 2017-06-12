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

## `class AgentSchedulerDbMixin(agents_db.AgentDbMixin)`

这是一个基础类，实现一些 agent 的封装功能

`agents_db.AgentDbMixin` 这个我在 **Neutron WSGI 之 agent** 中讲过

### 





