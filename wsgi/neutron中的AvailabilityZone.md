# neutron 中 AvailabilityZone 的实现

## 测试：

* 测试一：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/availability_zones -H 'Content-Type: application/json' -H 'X-Auth-Token: caba100684be40bab941b095356f14bb' | jq
```

结果：

```
{
  "availability_zones": [
    {
      "state": "available",
      "resource": "router",
      "name": "nova"
    },
    {
      "state": "available",
      "resource": "network",
      "name": "nova"
    }
  ]
}

```

* 测试二

```
curl -s -X GET http://172.16.100.106:9696//v2.0/agents -H 'Content-Type: application/json' -H 'X-Auth-Token: caba100684be40bab941b095356f14bb' | jq
```

结果：

```
{
  "agents": [
    {
      "binary": "neutron-dhcp-agent",
      "description": null,
      "availability_zone": "nova",
      "heartbeat_timestamp": "2017-06-03 14:33:11",
      "admin_state_up": true,
      "alive": true,
      "id": "58ea7075-d9e6-4070-9e57-bbce22335f2c",
      "topic": "dhcp_agent",
      "host": "localhost",
      "agent_type": "DHCP agent",
      "started_at": "2017-03-07 10:01:03",
      "created_at": "2017-03-07 10:01:03",
      "configurations": {
        "notifies_port_ready": true,
        "subnets": 2,
        "dhcp_lease_duration": 86400,
        "dhcp_driver": "neutron.agent.linux.dhcp.Dnsmasq",
        "networks": 1,
        "log_agent_heartbeats": false,
        "ports": 3
      }
    },
    {
      "binary": "neutron-l3-agent",
      "description": null,
      "availability_zone": "nova",
      "heartbeat_timestamp": "2017-06-03 14:33:19",
      "admin_state_up": true,
      "alive": true,
      "id": "66632c23-fc46-4c71-9722-983d0c000586",
      "topic": "l3_agent",
      "host": "localhost",
      "agent_type": "L3 agent",
      "started_at": "2017-03-07 10:01:07",
      "created_at": "2017-03-07 10:01:07",
      "configurations": {
        "agent_mode": "legacy",
        "gateway_external_network_id": "",
        "handle_internal_only_routers": true,
        "routers": 1,
        "interfaces": 2,
        "floating_ips": 0,
        "interface_driver": "openvswitch",
        "log_agent_heartbeats": false,
        "external_network_bridge": "",
        "ex_gw_ports": 1
      }
    },
    {
      "binary": "neutron-metadata-agent",
      "description": null,
      "availability_zone": null,
      "heartbeat_timestamp": "2017-06-03 14:33:30",
      "admin_state_up": true,
      "alive": true,
      "id": "7aba5cda-81f6-4a84-b846-1af29895f292",
      "topic": "N/A",
      "host": "localhost",
      "agent_type": "Metadata agent",
      "started_at": "2017-03-07 10:01:11",
      "created_at": "2017-03-07 10:01:11",
      "configurations": {
        "log_agent_heartbeats": false,
        "nova_metadata_port": 8775,
        "nova_metadata_ip": "172.16.100.106",
        "metadata_proxy_socket": "/opt/stack/data/neutron/metadata_proxy"
      }
    },
    {
      "binary": "neutron-openvswitch-agent",
      "description": null,
      "availability_zone": null,
      "heartbeat_timestamp": "2017-06-03 14:33:12",
      "admin_state_up": true,
      "alive": true,
      "id": "cc58ebc2-109e-4eda-b8a1-97ee551a0581",
      "topic": "N/A",
      "host": "localhost",
      "agent_type": "Open vSwitch agent",
      "started_at": "2017-03-07 10:01:04",
      "created_at": "2017-03-07 10:01:04",
      "configurations": {
        "ovs_hybrid_plug": true,
        "in_distributed_mode": false,
        "datapath_type": "system",
        "vhostuser_socket_dir": "/var/run/openvswitch",
        "tunneling_ip": "172.16.100.106",
        "arp_responder_enabled": false,
        "devices": 4,
        "ovs_capabilities": {
          "datapath_types": [
            "netdev",
            "system"
          ],
          "iface_types": [
            "geneve",
            "gre",
            "internal",
            "ipsec_gre",
            "lisp",
            "patch",
            "stt",
            "system",
            "tap",
            "vxlan"
          ]
        },
        "log_agent_heartbeats": false,
        "l2_population": false,
        "tunnel_types": [
          "vxlan"
        ],
        "extensions": [],
        "enable_distributed_routing": false,
        "bridge_mappings": {
          "public": "br-ex"
        }
      }
    }
  ]
}
```

## 实现

### 资源扩展

在 *neutron/extensions/availability_zone.py* 中实现。

1. 提供了访问 `availabilityzones` 的扩展；
2. 为 `agents` 资源增加了 `availabilityzones` 扩展；

### 后台接口

在 *neutron/db/agents_db.py* 中实现：

```
class AgentAvailabilityZoneMixin(az_ext.AvailabilityZonePluginBase):
    """Mixin class to add availability_zone extension to AgentDbMixin."""

    def _list_availability_zones(self, context, filters=None):
        result = {}
        query = self._get_collection_query(context, Agent, filters=filters)
        for agent in query.group_by(Agent.admin_state_up,
                                    Agent.availability_zone,
                                    Agent.agent_type):
            if not agent.availability_zone:
                continue
            if agent.agent_type == constants.AGENT_TYPE_DHCP:
                resource = 'network'
            elif agent.agent_type == constants.AGENT_TYPE_L3:
                resource = 'router'
            else:
                continue
            key = (agent.availability_zone, resource)
            result[key] = agent.admin_state_up or result.get(key, False)
        return result

    @db_api.retry_if_session_inactive()
    def get_availability_zones(self, context, filters=None, fields=None,
                               sorts=None, limit=None, marker=None,
                               page_reverse=False):
        """Return a list of availability zones."""
        # NOTE(hichihara): 'tenant_id' is dummy for policy check.
        # it is not visible via API.
        return [{'state': 'available' if v else 'unavailable',
                 'name': k[0], 'resource': k[1],
                 'tenant_id': context.tenant_id}
                for k, v in six.iteritems(self._list_availability_zones(
                                           context, filters))]

    @db_api.retry_if_session_inactive()
    def validate_availability_zones(self, context, resource_type,
                                    availability_zones):
        """Verify that the availability zones exist."""
        if not availability_zones:
            return
        if resource_type == 'network':
            agent_type = constants.AGENT_TYPE_DHCP
        elif resource_type == 'router':
            agent_type = constants.AGENT_TYPE_L3
        else:
            return
        query = context.session.query(Agent.availability_zone).filter_by(
                    agent_type=agent_type).group_by(Agent.availability_zone)
        query = query.filter(Agent.availability_zone.in_(availability_zones))
        azs = [item[0] for item in query]
        diff = set(availability_zones) - set(azs)
        if diff:
            raise az_ext.AvailabilityZoneNotFound(availability_zone=diff.pop())
```

这里看的比较清楚了，`get_availability_zones` 方法会调用 `_list_availability_zones`，`_list_availability_zones` 会访问 `agents` 的数据库来获取数据，这也是我们开始两个实验的目的。

# 参考

[OpenStack Neutron Availability Zone 简介](https://www.ibm.com/developerworks/cn/cloud/library/1607-openstack-neutron-availability-zone/)