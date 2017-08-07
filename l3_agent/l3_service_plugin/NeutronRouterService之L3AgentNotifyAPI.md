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