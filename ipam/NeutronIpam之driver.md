# Neutron Ipam 之 driver 

*neutron/ipam/driver.py*

这个模块实现了 Ipam 后台驱动的抽象类。

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