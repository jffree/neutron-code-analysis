# Neutron Ipam 之 IpamSubnetGroup

*neutron/ipam/driver.py*

*neutron/ipam/subnet_alloc.py*

## `class SubnetGroup(object)`

抽象类，只定义了一个抽象方法

### `def allocate(self, address_request)`

唯一的抽象方法

## `class IpamSubnetGroup(driver.SubnetGroup)`

### `def __init__(self, driver, subnet_ids)`

```
    def __init__(self, driver, subnet_ids):
        self._driver = driver
        self._subnet_ids = subnet_ids
```

### `def allocate(self, address_request)`



















