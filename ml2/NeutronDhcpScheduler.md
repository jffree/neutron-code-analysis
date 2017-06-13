# Neutron Dhcp Scheduler

在 `Ml2Plugin._setup_dhcp` 中：

```
    def _setup_dhcp(self):
        """Initialize components to support DHCP."""
        self.network_scheduler = importutils.import_object(
            cfg.CONF.network_scheduler_driver
        )
        self.add_periodic_dhcp_agent_status_check()
```

在 */etc/neutron/neutron.conf* 中，我们可以找到这个调度驱动的选项：

```
network_scheduler_driver = neutron.scheduler.dhcp_agent_scheduler.WeightScheduler
```

在 *neutron/scheduler/dhcp_agent_scheduler.py* 中：

```
class WeightScheduler(base_scheduler.BaseWeightScheduler, AutoScheduler):

    def __init__(self):
        super(WeightScheduler, self).__init__(DhcpFilter())
```

在 *neutron/scheduler/base_scheduler.py* 中：

```
class BaseWeightScheduler(BaseScheduler):
    """Choose agents based on load."""
 
    def __init__(self, resource_filter):
        self.resource_filter = resource_filter
 
    def select(self, plugin, context, resource_hostable_agents,
               resource_hosted_agents, num_agents_needed):
        chosen_agents = sorted(resource_hostable_agents,
                           key=attrgetter('load'))[0:num_agents_needed]
        return chosen_agents 
```

```
@six.add_metaclass(abc.ABCMeta)
class BaseScheduler(object):
    """The base scheduler (agnostic to resource type).                                                                                                                 
       Child classes of BaseScheduler must define the
       self.resource_filter to filter agents of
       particular type.
    """
    resource_filter = None

    @abc.abstractmethod
    def select(self, plugin, context, resource_hostable_agents,
               resource_hosted_agents, num_agents_needed):
        """Return a subset of agents based on the specific scheduling logic."""

    def schedule(self, plugin, context, resource):
        """Select and bind agents to a given resource."""
        if not self.resource_filter:
            return
        # filter the agents that can host the resource
        filtered_agents_dict = self.resource_filter.filter_agents(
            plugin, context, resource)
        num_agents = filtered_agents_dict['n_agents']
        hostable_agents = filtered_agents_dict['hostable_agents']
        hosted_agents = filtered_agents_dict['hosted_agents']
        chosen_agents = self.select(plugin, context, hostable_agents,
                                    hosted_agents, num_agents)
        # bind the resource to the agents
        self.resource_filter.bind(context, chosen_agents, resource['id'])
        return chosen_agents
```


从这里看，最重要的还是 `resource_filter`，也就是 `DhcpFilter()`

### `class DhcpFilter(base_resource_filter.BaseResourceFilter)`




