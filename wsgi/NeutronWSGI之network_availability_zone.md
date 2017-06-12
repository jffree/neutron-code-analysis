# Neutron WSGI 之 network_availability_zone

* 测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/networks -H 'Content-Type: application/json' -H 'X-Auth-Token: deffcb298bfc499f8524625b98af7b97' | jq
```

* extension：*neutron/extensions/network_availability_zone.py*

这个 extension 是为 `networks` 增加两个属性： `availability_zone_hints` 和 `availability_zones`。

* WSGI 的实现：*neutron/db/agentschedulers_db.py* 中的 `class AZDhcpAgentSchedulerDbMixin`

## `class AZDhcpAgentSchedulerDbMixin`

```
class AZDhcpAgentSchedulerDbMixin(DhcpAgentSchedulerDbMixin,
                                  network_az.NetworkAvailabilityZoneMixin):
    """Mixin class to add availability_zone supported DHCP agent scheduler."""

    def get_network_availability_zones(self, network):
        zones = {agent.availability_zone for agent in network.dhcp_agents}                                                                                             
        return list(zones)

```

## `NetworkAvailabilityZoneMixin`

```
class NetworkAvailabilityZoneMixin(net_az.NetworkAvailabilityZonePluginBase):
    """Mixin class to enable network's availability zone attributes."""
 
    def _extend_availability_zone(self, net_res, net_db):
        net_res[az_ext.AZ_HINTS] = az_ext.convert_az_string_to_list(
            net_db[az_ext.AZ_HINTS])
        net_res[az_ext.AVAILABILITY_ZONES] = ( 
            self.get_network_availability_zones(net_db))
 
    common_db_mixin.CommonDbMixin.register_dict_extend_funcs(
        attributes.NETWORKS, ['_extend_availability_zone']) 
```

看到这个 `common_db_mixin.CommonDbMixin.register_dict_extend_funcs` 是不是就比较熟悉了？

我写过一篇 **Neutron DB 中的公共方法**，里面有这个的介绍。

在构造 `networks` 资源的请求响应时，会调用这个注册的方法，来进行响应的构造。