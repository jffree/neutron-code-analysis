# Neutron Ipam 之 IpamSubnetManager

**subnet 地址分配的管理类，只负责与 ipam 相关的数据库交互**

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

### `def delete_allocation(self, session, ip_address)`

根据该子网的 ip 地址获取 `IpamAllocation` 数据库的记录，删除这条记录

### `def create(self, session)`

创建一个 `IpamSubnet` 的数据库记录。（类似于从 object 创建数据库记录）

### `def delete(cls, session, neutron_subnet_id)`

根据 subnet 的 id，删除一条 `IpamSubnet` 数据库记录（意味着删除从 ipam 分配的该子网）

### `def create_pool(self, session, pool_start, pool_end)`

创建一条 `IpamAllocationPool` 数据库记录，意味着为该子网增加一个地址池

### `def delete_allocation_pools(self, session)`

删除该子网的所有地址池记录。从 `IpamAllocationPool` 数据库中。