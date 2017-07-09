# Neutron Ml2 之 portbinding

## extension

*neutron/extensions/portbings.py*

`class Portbindings(extensions.ExtensionDescriptor)`

## Model

*neutron/plugins/ml2/models.py*

`class PortBinding(model_base.BASEV2)`

## 测试

```
neutron port-create --name simple --description 'This is a test port.' --device_owner compute:nova private --binding:profile type=dict foo=1 --binding:host_id localhost --binding:vnic_type normal
```

```
Created a new port:
+-----------------------+-----------------------------------------------------------------------------------------------------------+
| Field                 | Value                                                                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------+
| admin_state_up        | True                                                                                                      |
| allowed_address_pairs |                                                                                                           |
| binding:host_id       | localhost                                                                                                 |
| binding:profile       | {"foo": "1"}                                                                                              |
| binding:vif_details   | {"port_filter": true, "ovs_hybrid_plug": true}                                                            |
| binding:vif_type      | ovs                                                                                                       |
| binding:vnic_type     | normal                                                                                                    |
| created_at            | 2017-07-09T14:56:43Z                                                                                      |
| description           | This is a test port.                                                                                      |
| device_id             |                                                                                                           |
| device_owner          | compute:nova                                                                                              |
| extra_dhcp_opts       |                                                                                                           |
| fixed_ips             | {"subnet_id": "f61f47d3-2396-4528-bc70-bf761b5753cc", "ip_address": "10.0.0.8"}                           |
|                       | {"subnet_id": "6f78d1ea-ea8b-4680-b876-0852f3bd35e9", "ip_address":                                       |
|                       | "fdb9:ae91:869d:0:f816:3eff:fe82:c234"}                                                                   |
| id                    | cc33399e-b772-4b01-b595-f382e6ed8c7e                                                                      |
| mac_address           | fa:16:3e:82:c2:34                                                                                         |
| name                  | simple                                                                                                    |
| network_id            | 534b42f8-f94c-4322-9958-2d1e4e2edd47                                                                      |
| port_security_enabled | True                                                                                                      |
| project_id            | d4edcc21aaca452dbc79e7a6056e53bb                                                                          |
| revision_number       | 7                                                                                                         |
| security_groups       | e1f03790-837a-4057-8c6d-b124da9e3b7e                                                                      |
| status                | DOWN                                                                                                      |
| tenant_id             | d4edcc21aaca452dbc79e7a6056e53bb                                                                          |
| updated_at            | 2017-07-09T14:56:44Z                                                                                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------+
```

## port binding 在 Ml2 的实现



## 未查询到使用的关于 Port binding 的模块

*neutron/db/portbindings_db.py*

*neutron/db/portbindings_base.py*

## 参考

[Understanding ML2 Port Binding](https://www.openstack.org/videos/video/understanding-ml2-port-binding)

[OpenStack中实现混合Hypervisor原理剖析(by quqi99)](http://blog.csdn.net/quqi99/article/details/18318365)