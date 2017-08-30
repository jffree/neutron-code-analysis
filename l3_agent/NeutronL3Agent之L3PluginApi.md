# Neutron L3 Agent 之 L3PluginApi

## `class L3PluginApi(object)`

*neutron/agent/l3/agent.py*

```
    def __init__(self, topic, host):
        self.host = host
        target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(target)
```

l3 agent RPC Client，Server endpoint 为：`L3RpcCallback`

TOPIC : q-l3-plugin

### `def get_routers(self, context, router_ids=None)`

调用 RPC Server 端的 `sync_routers` 方法获取这些 router （如果这些 router 与该 host 上的 l3 agent 绑定）的数据

### `def get_router_ids(self, context)`

调用 RPC Server 端的 `get_router_ids` 方法，获取本机上的 router

### `def get_external_network_id(self, context)`

调用 Server 端的 `get_external_network_id` 方法获取 external network id

### `def update_floatingip_statuses(self, context, router_id, fip_statuses)`

调用 Server 端的 `update_floatingip_statuses` 更新 floating ip 的状态

```
FLOATINGIP_STATUS_ACTIVE = 'ACTIVE'
FLOATINGIP_STATUS_DOWN = 'DOWN'
FLOATINGIP_STATUS_ERROR = 'ERROR'
FLOATINGIP_STATUS_NOCHANGE = object()
```

### `def get_ports_by_subnet(self, context, subnet_id)`

调用 Server 端的 `get_ports_by_subnet` 方法，获取该 subnet 上的 port

### `def get_agent_gateway_port(self, context, fip_net)`

调用 Server 端的 `get_agent_gateway_port` 方法，获取 agent gateway port

### `def get_service_plugin_list(self, context)`

调用 Server 端的 `get_service_plugin_list`，获取 neutron-server 开启了的 service plugin 列表

### `def update_ha_routers_states(self, context, states)`

调用 Server 端的 `update_ha_routers_states` 方法，更新 ha router 的状态

```
TRANSLATION_MAP = {'master': constants.HA_ROUTER_STATE_ACTIVE,
                   'backup': constants.HA_ROUTER_STATE_STANDBY,
                   'fault': constants.HA_ROUTER_STATE_STANDBY}
```

### `def delete_agent_gateway_port(self, context, fip_net)`

调用 Server 端的 `delete_agent_gateway_port` 方法，删除 agent gateway port

### `def process_prefix_update(self, context, prefix_update)`

调用 Server 端的 `process_prefix_update` 方法，









