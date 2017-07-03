# Neutron Ipam 之 IpamSubnetManager

subnet 地址分配的实际管理类，负责与 ipam 相关的数据库交互

*neutron/ipam/drivers/neutrondb_ipam/db_api.py*

涉及到的数据库：

* `IpamSubnet`：绑定了子网的 id 与 本数据库的 Id

* `IpamAllocationPool`：绑定了 `IpamSubnet` 数据库的 id，记录了该子网的地址池

* `IpamAllocation`：绑定了 `IpamSubnet` 数据库的 id，记录了该子网的 ip 地址分配记录

## `class IpamSubnetManager(object)`

### `def load_by_neutron_subnet_id(cls, session, neutron_subnet_id)`

根据子网的 id，加载数据库 `IpamSubnet` 的一条记录

### `def __init__(self, ipam_subnet_id, neutron_subnet_id)`

1. `ipam_subnet_id` 指 `IpamSubnet` 数据库中的 id
2. `neutron_subnet_id` 指 subnet 数据的 id

### `def neutron_id(self)`

属性方法，返回 `self._neutron_subnet_id`

### `def check_unique_allocation(self, session, ip_address)`

通过检查 `IpamAllocation` 数据库记录，确定该子网的这个 ip 地址（`ip_address`）是否已经被分配。

### `def list_allocations(self, session, status='ALLOCATED')`

在 `IpamAllocation` 数据库中获取该子网已经分配的 Ip 地址的记录。

### `def list_pools(self, session)`

在 `IpamAllocationPool` 数据库中获取该子网所拥有的地址池。

### `def create_allocation(self, session, ip_address, status='ALLOCATED')`

创建一个 `IpamAllocation` 的数据库记录，也就是从子网中分配了一个地址











