# Neutron Ml2 type driver 之 geneve

## `class GeneveAllocation(model_base.BASEV2)`

geneve 分配的数据库

## `class GeneveEndpoints(model_base.BASEV2)`

geneve endpoint 数据库


## `class GeneveTypeDriver(type_tunnel.EndpointTunnelTypeDriver)`

*neutron/plugins/ml2/drivers/type_geneve.py*

```
    def __init__(self):
        super(GreTypeDriver, self).__init__(
            gre_model.GreAllocation, gre_model.GreEndpoints)
```

## `def get_type(self)`

返回 geneve

### `def initialize(self)`

调用 `_initialize` 实现。
 
### `def get_endpoints(self)`

调用 `_get_endpoints` 实现。

### `def add_endpoint(self, ip, host)`

增加一个 endpoint

### `def get_mtu(self, physical_network=None)`

获取 geneve network 的 mtu