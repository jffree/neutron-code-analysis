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
+-----------------------+-----------------------------------------------------------------------------------------------------------+
| Field                 | Value                                                                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------+
| admin_state_up        | True                                                                                                      |
| allowed_address_pairs |                                                                                                           |
| binding:host_id       | localhost                                                                                                 |
| binding:profile       | {"foo": "1"}                                                                                              |
| binding:vif_details   | {}                                                                                                        |
| binding:vif_type      | binding_failed                                                                                            |
| binding:vnic_type     | normal                                                                                                    |
| created_at            | 2017-07-09T13:24:56Z                                                                                      |
| description           | This is a test port.                                                                                      |
| device_id             |                                                                                                           |
| device_owner          | compute:nova                                                                                              |
| extra_dhcp_opts       |                                                                                                           |
| fixed_ips             | {"subnet_id": "f61f47d3-2396-4528-bc70-bf761b5753cc", "ip_address": "10.0.0.8"}                           |
|                       | {"subnet_id": "6f78d1ea-ea8b-4680-b876-0852f3bd35e9", "ip_address":                                       |
|                       | "fdb9:ae91:869d:0:f816:3eff:fe0e:5dc5"}                                                                   |
| id                    | 41272709-e28f-4af5-8724-fc7d6f687225                                                                      |
| mac_address           | fa:16:3e:0e:5d:c5                                                                                         |
| name                  | simple                                                                                                    |
| network_id            | 534b42f8-f94c-4322-9958-2d1e4e2edd47                                                                      |
| port_security_enabled | True                                                                                                      |
| project_id            | d4edcc21aaca452dbc79e7a6056e53bb                                                                          |
| revision_number       | 7                                                                                                         |
| security_groups       | e1f03790-837a-4057-8c6d-b124da9e3b7e                                                                      |
| status                | DOWN                                                                                                      |
| tenant_id             | d4edcc21aaca452dbc79e7a6056e53bb                                                                          |
| updated_at            | 2017-07-09T13:24:56Z                                                                                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------
```

## 未查询到使用的关于 Port binding 的模块

*neutron/db/portbindings_db.py*

*neutron/db/portbindings_base.py*