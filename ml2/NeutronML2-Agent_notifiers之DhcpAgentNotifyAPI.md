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