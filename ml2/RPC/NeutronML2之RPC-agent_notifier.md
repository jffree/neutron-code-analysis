# Neutron Ml2 之 RPC-agent_notifier

在 ml2 中：

```
    def _start_rpc_notifiers(self):
        """Initialize RPC notifiers for agents."""
        self.notifier = rpc.AgentNotifierApi(topics.AGENT)
        self.agent_notifiers[const.AGENT_TYPE_DHCP] = (
            dhcp_rpc_agent_api.DhcpAgentNotifyAPI()
        )
```

self.agent_notifiers 是在 `AgentSchedulerDbMixin` 中定义的，模块位于：*neutron/db/agentschedulers_db.py*