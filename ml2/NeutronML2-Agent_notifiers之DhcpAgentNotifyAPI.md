# Neutron ML2 agent_notifiers 之 DhcpAgentNotifyAPI

*neutron/api/rpc/agentnotifiers/dhcp_rpc_agent_api.py*

## `class DhcpAgentNotifyAPI(object)`

plugin 用这些接口来通知 dhcp agent

### `def __init__(self, topic=topics.DHCP_AGENT, plugin=None)`

1. 创建一个 rpc client（topic : `dhcp_agent`; version : `1.0`）
2. 调用 Neutron 回调系统注册监听事件：
 1. `resources.ROUTER_INTERFACE, events.AFTER_CREATE`
 2. `resources.ROUTER_INTERFACE, events.AFTER_DELETE`
 3. `resources.NETWORK, events.BEFORE_RESPONSE, events.AFTER_CREATE, events.AFTER_UPDATE, events.AFTER_DELETE`
 4. `resources.NETWORKS, events.BEFORE_RESPONSE`
 5. `resources.PORT, events.BEFORE_RESPONSE, events.AFTER_CREATE, events.AFTER_UPDATE, events.AFTER_DELETE`
 6. `resources.PORTS, events.BEFORE_RESPONSE`
 7. `resources.SUBNET, events.BEFORE_RESPONSE, events.AFTER_CREATE, events.AFTER_UPDATE, events.AFTER_DELETE`
 8. `resources.SUBNETS, events.BEFORE_RESPONSE`

### `def plugin(self)`

属性方法，返回 core plugin 实例

### `def _cast_message(self, context, method, payload, host,                      topic=topics.DHCP_AGENT)`

使用 cast 方式在指定的 server（host）上的 topic（`dhcp_agent`） 上调用 method 方法。

### `def _fanout_message(self, context, method, payload)`

以 fanout 的方法调用所有监听的 server 上的方法

### `def agent_updated(self, context, admin_state_up, host)`

通过 `_cast_message` 调用 `agent_updated` 方法

### `def network_added_to_agent(self, context, network_id, host)`

通过 `_cast_message` 调用 `network_create_end` 方法

### `def network_removed_from_agent(self, context, network_id, host)`

通过 `_cast_message` 调用 `network_delete_end` 方法

### `def _schedule_network(self, context, network, existing_agents)`

1. 调用 plugin 的 `schedule_network` 方法为 network 绑定新的 agent
2. 通过 `_cast_message` 在所有新绑定的 agent 上调用 `network_create_end` 方法
3. 返回所有与改网络资源绑定的 agent

### `def _get_enabled_agents(self, context, network, agents, method, payload)`

根据 `network` 和 `agents` 获取可以提供该 `network` 服务的 agent 列表

### `def _notify_agents(self, context, method, payload, network_id)`

1. 判断该 rpc 动作是 fanout 模式还是 cast 模式
2. 若是 fanout 模式，则直接调用 `_fanout_message` 来做调用
3. 若是 cast 模式，对于新创建的资源（port、network）调用 `_schedule_network` 来绑定新的 agent
4. 调用 `_get_enabled_agents` 过滤出所有与 network 绑定的 agent 中可以提供服务的 agent
5. 调用 `_cast_message` 在这些 agent 上调用相应的方法

### `def _after_router_interface_created(self, resource, event, trigger, **kwargs)`

该方法在 `__init__` 方法中被注册到了 Neutron 的回调系统中

```
registry.subscribe(self._after_router_interface_created,
                           resources.ROUTER_INTERFACE, events.AFTER_CREATE)
```

该方法直接调用 `self._notify_agents` 方法

### `def _after_router_interface_deleted(self, resource, event, trigger, **kwargs)`

该方法与 `_after_router_interface_created` 类似

### `def notify(self, context, data, method_name)`

也是对 `_notify_agents` 的调用