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
3. 








