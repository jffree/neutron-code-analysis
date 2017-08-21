# Neutron router service 之 `L3AgentNotifyAPI`

*neutron/api/rpc/agentnotifiers/l3_rpc_agent_api.py*

## `class L3AgentNotifyAPI(object)`

```
    def __init__(self, topic=topics.L3_AGENT):
        target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(target)
```

### `def _notification_host(self, context, method, host, use_call=False, **kwargs)`

对于指定 host 上的 l3 agent 发送通知或调用

### `def _agent_notification(self, context, method, router_ids, operation, shuffle_agents)`

1. 调用 `l3_router_nat.get_hosts_to_notify` 根据 router_id 获取所有需要通知的 l3 agent 
2. 针对所有的 l3 agent 发送通知

### `def _agent_notification_arp(self, context, method, router_id, operation, data)`

广播通知所有的 l3 agent 有关 arp 的数据

### `def _notification(self, context, method, router_ids, operation, shuffle_agents, schedule_routers=True)`

1. 若是支持 `l3_agent_scheduler` extension，则只通知拥有该 router 的 l3 agent
2. 若是不支持 `l3_agent_scheduler` 则广播通知所有的 l3 agent

### `def _notification_fanout(self, context, method, router_id=None, **kwargs)`

广播通知所有的 l3 agent

### `def agent_updated(self, context, admin_state_up, host)`

想特定的 Host 上发送 RPC 消息。

### `def router_deleted(self, context, router_id)`

发送 RPC 广播消息（某个 router 被删除）。

### `def routers_updated(self, context, router_ids, operation=None, data=None, shuffle_agents=False, schedule_routers=True)`

发送 router 更新的消息

### `def add_arp_entry(self, context, router_id, arp_table, operation=None)`

发送增加 arp 记录的 RPC 消息

### `def del_arp_entry(self, context, router_id, arp_table, operation=None)`

发送删除 arp 记录的 RPC 消息

### `def delete_fipnamespace_for_ext_net(self, context, ext_net_id)`

删除 fip namespace 的 RPC 消息

### `def router_removed_from_agent(self, context, router_id, host)`

发送 router 移除的 RPC 消息

### `def router_added_to_agent(self, context, router_ids, host)`

发送在某个 agent 上增加 router 的 RPC 消息

### `def routers_updated_on_host(self, context, router_ids, host)`

发送某个 agent 上 router 更新的 RPC 消息

## `class L3RpcNotifierMixin(object)`

在  `L3AgentNotifyAPI` 的基础上发送 RPC 消息

```
    def __new__(cls):
        L3RpcNotifierMixin._subscribe_callbacks()
        return object.__new__(cls)
```

### `def _subscribe_callbacks()`

* 通过 neutron 的 callback 系统订阅感兴趣资源的消息：
 1. PORT: AFTER_DELETE: _notify_routers_callback
 2. SUBNET_GATEWAY: AFTER_UPDATE: _notify_subnet_gateway_ip_update
 3. SUBNETPOOL_ADDRESS_SCOPE: AFTER_UPDATE: _notify_subnetpool_address_scope_update

### `def l3_rpc_notifier(self)`

属性方法，返回 `L3AgentNotifyAPI` 的实例

### `def notify_router_updated(self, context, router_id, operation=None)`

发送单个 router 更新的 RPC 消息

### `def notify_routers_updated(self, context, router_ids, operation=None, data=None)`

发送多个 router 更新的 RPC 消息

### `def notify_router_deleted(self, context, router_id)`

发送 router 删除的 RPC 消息

### `def _notify_routers_callback(resource, event, trigger, **kwargs)`

当有 port 资源删除的时候，会触发此方法，进一步发送 router 更新的 RPC 消息。（`L3_NAT_db_mixin.notify_routers_updated`）

### `def _notify_subnet_gateway_ip_update(resource, event, trigger, **kwargs)`

当某一子网的网关 ip 发生变化时，发送 router 更新的 RPC 消息。（`L3RpcNotifierMixin.notify_router_updated`）

### `def _notify_subnetpool_address_scope_update(resource, event, trigger, **kwargs)`

当某一子网的地址范围发生变化时，发送 router 更新的 RPC 消息。（`L3_NAT_db_mixin.notify_routers_updated`）