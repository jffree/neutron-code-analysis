# Neutron Ipam 之 IpamSubnetManager

*neutron/ipam/drivers/neutrondb_ipam/db_api.py*

涉及到的数据库：

* `IpamSubnet`：绑定了子网的 id 与 本数据库的 Id

* `IpamAllocationPool`：绑定了 `IpamSubnet` 数据库的 id，记录了该子网的地址池

* `IpamAllocation`：绑定了 `IpamSubnet` 数据库的 id，记录了该子网的 ip 地址分配记录

## `class IpamSubnetManager(object)`

### `def load_by_neutron_subnet_id(cls, session, neutron_subnet_id)`

根据子网的 id，加载数据库 `IpamSubnet` 的一条记录




























