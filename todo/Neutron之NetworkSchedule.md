# Neutron 之 network schedule

network schedule 是指 network 资源与 dhcp agent 的绑定情况

## `class DhcpAgentSchedulerDbMixin(dhcpagentscheduler.DhcpAgentSchedulerPluginBase, AgentSchedulerDbMixin)`

*neutron/db/agentscheduler.py*

### `def auto_schedule_networks(self, context, host)`



## `class AutoScheduler(object)`

*neutron/scheduler/dhcp_agent_scheduler.py*


### `def auto_schedule_networks(self, plugin, context, host)`



## `class WeightScheduler(base_scheduler.BaseWeightScheduler, AutoScheduler)`

*neutron/scheduler/dhcp_agent_scheduler.py*

```
    def __init__(self):
        super(WeightScheduler, self).__init__(DhcpFilter())
```
这里在初始化时，指明了 `self.resource_filter` 为 `DhcpFilter()`


## `class DhcpFilter(base_resource_filter.BaseResourceFilter)`

*neutron/scheduler/dhcp_agent_scheduler.py*

### `def bind(self, context, agents, network_id)`






