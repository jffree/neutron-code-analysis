# Neutron Ipam 之 NeutronDbPool

将 subnetpool 数据库的记录转化为一个对象 `NeutronDbPool`，类似于 Neutron 的 object 一样。

*neutron/ipam/driver.py*

*neutron/ipam/drivers/neutrondb_ipam/driver.py*

## `class Pool(object)`

```
@six.add_metaclass(abc.ABCMeta)
class Pool(object)
```

这个类定义了一系列的抽象方法：`allocate_subnet`、`get_subnet`、`update_subnet`、`remove_subnet`、`get_allocator`，这些方法都要在其子类中实现。

### `__init__`

```
    def __init__(self, subnetpool, context):
        """Initialize pool

        :param subnetpool: SubnetPool of the address space to use.
        :type subnetpool: dict
        """
        self._subnetpool = subnetpool
        self._context = context
```

### `def get_instance(cls, subnet_pool, context)`

即在 ipam 的实现驱动，该驱动在 */etc/neutron/neutron.conf* 中定义 `ipam_driver`

```
# Neutron IPAM (IP address management) driver to use. By default, the reference
# implementation of the Neutron IPAM driver is used. (string value)
#ipam_driver = internal
```

在 *setup.cfg* 中：

```
neutron.ipam_drivers =
    fake = neutron.tests.unit.ipam.fake_driver:FakeDriver
    internal = neutron.ipam.drivers.neutrondb_ipam.driver:NeutronDbPool
```

我们看一下这个 `NeutronDbPool` ：

```
class NeutronDbPool(subnet_alloc.SubnetAllocator)
```

```
class SubnetAllocator(driver.Pool)
```

追踪下来，其实这个 driver 是本类 `Pool` 的一个实例。

### `def get_subnet_request_factory(self)`

```
    def get_subnet_request_factory(self):
        return ipam_req.SubnetRequestFactory
```

### `def get_address_request_factory(self)`

```
    def get_address_request_factory(self):
        return ipam_req.AddressRequestFactory
```

### `def needs_rollback(self)`

```
    def needs_rollback(self):
        return True
```

## `class SubnetAllocator(driver.Pool)`

*neutron/ipam/subnet_alloc.py*

在 `Pool` 类的基础上实现了一些

### `def __init__(self, subnetpool, context)`

```
    def __init__(self, subnetpool, context):
        super(SubnetAllocator, self).__init__(subnetpool, context)
        self._sp_helper = SubnetPoolHelper()
```

### `def allocate_subnet(self, request)`

1. 判断分配子网请求的 `prefixlen` 属性在子网池的 `max_prefixlen` 和 `min_prefixlen` 的范围之间
2. 若请求为 `AnySubnetRequest` 类型，则调用 `_allocate_any_subnet` 方法
3. 若请求为 `SpecificSubnetRequest` 类型，则调用 `_allocate_specific_subnet` 方法


### `def _allocate_any_subnet(self, request)`

1. 调用 `_lock_subnetpool` 锁住当前的数据库记录，防止同时进行两次子网的分配操作。
2. 调用 `_check_subnetpool_tenant_quota` 检查这次请求是否满足 quota 的限制
3. 调用 `_get_available_prefix_list` 获取当前子网池中可分配的 `cidr`
4. 从可用的子网池中分配子网
5. 调用 `ipam_utils.generate_pools` 



### `def _lock_subnetpool(self)`

以更新 `SubnetPool` 数据库的 `hash` 属性来将当前的这个数据库记录锁住。

### `def _check_subnetpool_tenant_quota(self, tenant_id, prefixlen)`

1. 调用 `SubnetPoolHelper.ip_version_subnetpool_quota_unit` 获取 quota_unit
2. 获取该 `SubnetPool` 数据库记录的 `default_quota` 属性（限制用户可申请的地址池个数）
3. 若是 `default_quota` 属性存在，则调用 `_allocations_used_by_tenant` 获取当前租户所拥有的所有的 Ip 地址的个数
4. 获取当前用户所拥有的 Ip 地址个数后，调用 `_num_quota_units_in_prefixlen` 获取这次请求需要的 Ip 地址个数
5. 若是当前请求的 IP 地址个数和当前租户已经拥有的 Ip 地址个数超过了 quota 限制，则引发异常


### `def _allocations_used_by_tenant(self, quota_unit)`

1. 查询 `Subnet` 数据库，获得当前租户从该子网池中分配出来的所有子网
2. 调用 `_num_quota_units_in_prefixlen` 计算当前租户的所用子网中的 ip 地址个数

### `def _num_quota_units_in_prefixlen(self, prefixlen, quota_unit)`

```
    def _num_quota_units_in_prefixlen(self, prefixlen, quota_unit):                                                                                                
        return math.pow(2, quota_unit - prefixlen)
```

这个方法用来计算当前 cidr 所拥有的 Ip 地址个数。（例：2^(32-16)）

### `def _get_available_prefix_list(self)`

1. 调用 `_get_allocated_cidrs` 获取已经分配出去的子网的 `cidr`
2. 调用 `netaddr.IPSet` 获取当前子网池可用的 `cidr`


### `def _get_allocated_cidrs(self)`

查询从当前子网池中所有分配出去的子网的 `cidr`，并按照 `cidr` 中的 `prefixlen` 进行由大到小的排序。




## `class NeutronDbPool(subnet_alloc.SubnetAllocator)`

子网池实现后端

### `def get_subnet(self, subnet_id)`

类方法，获取 `NeutronDbSubent` 描述的一个 subnet 数据库记录

```
    def get_subnet(self, subnet_id):
        return NeutronDbSubnet.load(subnet_id, self._context)
```

### `def allocate_subnet(self, subnet_request)`

1. 若本实例的 `_subnetpool` 不为空，则调用父类的 `allocate_subnet` 方法























