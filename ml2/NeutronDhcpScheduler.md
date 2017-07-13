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

## `class BaseScheduler(object)`

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

抽象基类，主要看一下 `schedule` 方法的实现：

1. 调用 `self.resource_filter.filter_agents` 选择可以绑定 resource 的 agent
2. 调用 `self.select` 对刚才获取的 agent 列表进行一个排序选择
3. 调用 `self.resource_filter.bind` 进行 resource 与 agent 的绑定

## `class BaseWeightScheduler(BaseScheduler)`

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

`BaseWeightScheduler` 实现了 `BaseScheduler` 的 `select` 方法，就是根据 agent 的 `load` 属性进行排序。这里的 `load` 是指该 agent 的负载，即该 agent 已经绑定了多少个 network。

* 从这里看，最重要的还是 `resource_filter`，也就是 `DhcpFilter()`

## `class DhcpFilter(base_resource_filter.BaseResourceFilter)`

### `def _get_dhcp_agents_hosting_network(self, plugin, context, network)`

1. 获取配置 `cfg.CONF.dhcp_agents_per_network` 该配置用于指定每个网络可以绑定到几个 dhcp agent 上面，默认为 1。
2. 调用 `plugin.get_dhcp_agents_hosting_networks` 也就是 `DhcpAgentSchedulerDbMixin.get_dhcp_agents_hosting_networks` 根据 `network_ids` 和 `hosts` 获取与之绑定的处于活动状态的 agent
3. 若是已经绑定的 `hosts` 的数量大于配置中设定的数量，则返回空
4. 若是小于则返回已经绑定的 agents

### `def _get_active_agents(self, plugin, context, az_hints)`

根据 `agent_type:'DHCP agent'` 、`admin_state_up:True`、`availability_zone=az_hints` 调用 `plugin.get_agents_db` 来获取活动的 dhcp agent

### `def _filter_agents_with_network_access(self, hostable_agents, plugin, context, network)`

在 `hostable_agents` 中过滤出来可挂载该 network 的 dhcp agent

### `def _get_network_hostable_dhcp_agents(self, plugin, context, network)`

1. 调用 `_get_dhcp_agents_hosting_network` 获取该 network 已经绑定的 agent
2. 调用 `_get_active_agents` 获取已启动的 dhcp agent
3. 在活动的 dhcp agent 列表中获取那些未绑定该 network 且活动的 dhcp agent
4. 调用 `_filter_agents_with_network_access` 对 dhcp agent 做进一步的过滤操作
5. 返回结果：`{'n_agents': n_agents, 'hostable_agents': hostable_dhcp_agents,                'hosted_agents': hosted_agents} `，启动 `n_agents` 指可以绑定的 agent 数量；`hostable_agents` 指可以绑定的 agent；`hosted_agents`指已经绑定的 agent

### `def filter_agents(self, plugin, context, network)`

直接调用 `_get_network_hostable_dhcp_agents`

### `def bind(self, context, agents, network_id)`

1. 根据 `agents` 和 `network_id` 创建 `NetworkDhcpAgentBinding` 的数据库记录（绑定记录）
2. 调用 `super(DhcpFilter, self).bind(context, bound_agents, network_id)` 更新这些 agents 的负载 `load+1`。

## `class AutoScheduler(object)`

这个类只实现了一个方法：

### `def auto_schedule_networks(self, plugin, context, host)`

**作用：**为网络绑定合适的 dhcp agent

`dhcp_agents_per_network`：每个网络可以有几个 dhcp agent 负责。在 *neutron.conf* 中定义：`dhcp_agents_per_network = 1`

* 为网络绑定 dhcp agent 需要考虑一下几点：
 1. 该网络下必须有子网允许绑定 dhcp （`enable_dhcp`）
 2. dhcp agent 必须是活动的
 3. 若该子网中有 `segment_id` 属性，则该子网必须绑定在与该 `segment_id` 绑定的 `host` 上的 dhcp agent 上
 4. 若该子网中没有 `segment_id` 属性，则该子网绑定的 dhcp agent 的数量需要小于等于 `dhcp_agents_per_network` 的设定值
 5. dhcp agent 与该网络的 `availability_zones` 必须相同

最后调用 `resource_filter.bind` 实现 dhcp agent 与 network 的绑定

# 参考

[OpenStack Neutron Availability Zone 简介](https://www.ibm.com/developerworks/cn/cloud/library/1607-openstack-neutron-availability-zone/)