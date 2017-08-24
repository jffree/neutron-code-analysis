# Neutron Router Service 之 Router_availability_zone extension

## extension

*neutron/extensions/router_availability_zone.py*

为 router 增加 `availability_zones` 和 `availability_zone_hints` 属性

```
@six.add_metaclass(abc.ABCMeta)
class RouterAvailabilityZonePluginBase(object):

    @abc.abstractmethod
    def get_router_availability_zones(self, router):
        """Return availability zones which a router belongs to."""
```

## WSGI 逻辑实现

*neutron/db/l3_agentschedulers_db.py*

### `class AZL3AgentSchedulerDbMixin(L3AgentSchedulerDbMixin, router_az.RouterAvailabilityZonePluginBase)`

```
class AZL3AgentSchedulerDbMixin(L3AgentSchedulerDbMixin,
                                router_az.RouterAvailabilityZonePluginBase):
    """Mixin class to add availability_zone supported l3 agent scheduler."""

    def get_router_availability_zones(self, router):
        return list({agent.availability_zone for agent in router.l3_agents})
```

返回与 router 绑定的 l3 agent 的 az 属性
