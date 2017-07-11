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

## `class AgentSchedulerDbMixin(agents_db.AgentDbMixin)`

```
    # agent notifiers to handle agent update operations;
    # should be updated by plugins;
    agent_notifiers = {
        constants.AGENT_TYPE_DHCP: None,
        constants.AGENT_TYPE_L3: None,
        constants.AGENT_TYPE_LOADBALANCER: None,
    }
```






















