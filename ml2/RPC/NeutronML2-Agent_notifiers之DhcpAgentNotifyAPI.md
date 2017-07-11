# Neutron ML2 agent_notifiers 之 DhcpAgentNotifyAPI

*neutron/api/rpc/agentnotifiers/dhcp_rpc_agent_api.py*

## `class DhcpAgentNotifyAPI(object)`

plugin 用这些接口来通知 dhcp agent

```
    VALID_RESOURCES = ['network', 'subnet', 'port']
    VALID_METHOD_NAMES = ['network.create.end',
                          'network.update.end',
                          'network.delete.end',
                          'subnet.create.end',
                          'subnet.update.end',
                          'subnet.delete.end',
                          'port.create.end',
                          'port.update.end',                                                                                                                           
                          'port.delete.end']
```

### `def __init__(self, topic=topics.DHCP_AGENT, plugin=None)`

1. 创建一个 rpc client（topic : `dhcp_agent`; version : `1.0`）
2. 调用 Neutron 回调系统注册监听事件：
 1. `resources.ROUTER_INTERFACE, events.AFTER_CREATE, _after_router_interface_created`
 2. `resources.ROUTER_INTERFACE, events.AFTER_DELETE, _after_router_interface_deleted`
 3. `resources.NETWORK, events.BEFORE_RESPONSE, _send_dhcp_notification`
 4. `resources.NETWORKS, events.BEFORE_RESPONSE, _send_dhcp_notification`
 5. `resources.PORT, events.BEFORE_RESPONSE, _send_dhcp_notification`
 6. `resources.PORTS, events.BEFORE_RESPONSE, _send_dhcp_notification`
 7. `resources.SUBNET, events.BEFORE_RESPONSE, _send_dhcp_notification`
 8. `resources.SUBNETS, events.BEFORE_RESPONSE, _send_dhcp_notification`
 9. `resources.NETWORK, [events.AFTER_CREATE, events.AFTER_UPDATE, events.AFTER_DELETE], _native_event_send_dhcp_notification`
 10. `resources.PORT, [events.AFTER_CREATE, events.AFTER_UPDATE, events.AFTER_DELETE], _native_event_send_dhcp_notification`
 11. `resources.SUBNET, [events.AFTER_CREATE, events.AFTER_UPDATE, events.AFTER_DELETE], _native_event_send_dhcp_notification`

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

* 参数说明：
 1. `context`：
 2. `method`：准备通过 RPC 调用的 agent 的方法
 3. `playload`：传递给 RPC 方法的参数
 4. `network_id`：与此次操作相关的网络资源的 id

* 作用：
 1. 根据调用的 RPC 的方法判断是 fanout 还是 cast 模式；
 2. fanout 模式是调用 `_fanout_message` 做进一步的处理；
 3. 若是采用 cast 模式，判断该模式下的 topic，再调用 `_cast_message` 做进一步的处理 

1. 调用 `utils.is_extension_supported` 判断 core plugin 是否支持 `dhcp_agent_scheduler`
2. 判断该 rpc 动作是 fanout 模式还是 cast 模式
3. 若是 fanout 模式，则直接调用 `_fanout_message` 来做调用
4. 若是 cast 模式，对于新创建的资源（port、network）调用 `_schedule_network` 来绑定新的 agent
5. 调用 `_get_enabled_agents` 过滤出所有与 network 绑定的 agent 中可以提供服务的 agent
6. 调用 `_cast_message` 在这些 agent 上调用相应的方法

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