# Neutron Ipam 之 NeutronDbSubnet

将 subnet 数据库的记录转化为一个对象 `NeutronDbSubnet`，类似于 Neutron 的 object 一样。

*neutron/ipam/driver.py*

*neutron/ipam/drivers/neutrondb_ipam/driver.py*

## `class Subnet(object)`

抽象基类，定义了三个抽象方法：

### `def allocate(self, address_request)`

分配 Ip

### `def deallocate(self, address)`

回收 Ip

### `def get_details(self)`

获取该子网的详细信息

## `class NeutronDbSubnet(ipam_base.Subnet)`

### `def load(cls, neutron_subnet_id, ctx)`

类方法

1. 调用 `IpamSubnetManager.load_by_neutron_subnet_id` 根据子网 id 记载数据库 `IpamSubnet` 的一条记录
2. 根据 `IpamSubnet` 加载该子网的所有子网池（`IpamAllocationPool`）
3. 调用 `_fetch_subnet` 获取子网的数据库记录
4. 通过上述获得的消息，构造该类的一个实例，用来表示一个子网。

### `def _fetch_subnet(cls, context, id)`

类方法

通过调用 ml2 的 `_get_subnet` 获取子网的数据库记录