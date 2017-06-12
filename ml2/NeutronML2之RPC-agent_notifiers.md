# Neutron ML2 之 RPC agent_notifiers

```
    def _start_rpc_notifiers(self):
        """Initialize RPC notifiers for agents."""
        self.notifier = rpc.AgentNotifierApi(topics.AGENT)
        self.agent_notifiers[const.AGENT_TYPE_DHCP] = (
            dhcp_rpc_agent_api.DhcpAgentNotifyAPI()
        )
```

`agent_notifiers` 是在 `AgentSchedulerDbMixin` 这个类中定义的。

这个类位于 *neutron/db/agentschedulers_db.py*

我们来看一下这个模块中的继承关系：

```
class AgentSchedulerDbMixin(agents_db.AgentDbMixin)

class DhcpAgentSchedulerDbMixin(dhcpagentscheduler
                                .DhcpAgentSchedulerPluginBase,
                                AgentSchedulerDbMixin)

class AZDhcpAgentSchedulerDbMixin(DhcpAgentSchedulerDbMixin,
                                  network_az.NetworkAvailabilityZoneMixin)
```

关于 `agents_db.AgentDbMixin` 请参考我写的 **Neutron WSGI 中的 agent**

关于 `network_availability_zone` 请参考我写的 **Neutron WSGI 之 network_availability_zone**


## `AZDhcpAgentSchedulerDbMixin` 与 `NetworkAvailabilityZoneMixin` 

这俩类与 `network_availability_zone` 有关 

## ``
















