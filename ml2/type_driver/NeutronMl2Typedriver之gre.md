# Neutron Ml2 type driver 之 gre

## `class GreAllocation(model_base.BASEV2)`

*neutron/db/modules/plugins/ml2/gre_allocation_endpoints.py*

gre 分配的数据库

## `class GreEndpoints(model_base.BASEV2)`

*neutron/db/modules/plugins/ml2/gre_allocation_endpoints.py*

gre endpoint 数据库


## `class LocalTypeDriver(api.TypeDriver)`

*neutron/plugins/ml2/drivers/type_gre.py*

```
    def __init__(self):
        super(GreTypeDriver, self).__init__(
            gre_model.GreAllocation, gre_model.GreEndpoints)
```

## `def get_type(self)`

返回 gre

### `def initialize(self)`

调用 `_initialize` 实现。
 
### `def get_endpoints(self)`

调用 `_get_endpoints` 实现。

### `def add_endpoint(self, ip, host)`

增加一个 endpoint

### `def get_mtu(self, physical_network=None)`

获取 gre network 的 mtu