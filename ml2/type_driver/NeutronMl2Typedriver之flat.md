# Neutron Ml2 type driver 之 flat

## `class FlatAllocation(model_base.BASEV2)`

记录 flat 分配的数据库。

*neutron/db/models/plugins/ml2/flatallocation.py*

```
MariaDB [neutron]> select * from ml2_flat_allocations;
+------------------+
| physical_network |
+------------------+
| public           |
+------------------+
```

## `class FlatTypeDriver(helpers.BaseTypeDriver)`

*neutron/plugins/ml2/drivers/type_flat.py*

```
    def __init__(self):
        super(FlatTypeDriver, self).__init__()
        self._parse_networks(cfg.CONF.ml2_type_flat.flat_networks)
```

### `def _parse_networks(self, entries)`

解析 `cfg.CONF.ml2_type_flat.flat_networks` 的配置（用于指明 flat network 可以创建在那些 physical network 只上，* 代表着任意）。

### `def get_type(self)`

返回 `flat`

### `def initialize(self)`

```
    def initialize(self):
        LOG.info(_LI("ML2 FlatTypeDriver initialization complete"))
```

### `def is_partial_segment(self, segment)`

返回 False

### `def validate_provider_segment(self, segment)`

当创建 flat 类型的 provider network 时，调用此方法验证 segment 的正确性

*physical_network* 参数必须存在

### `def reserve_provider_segment(self, session, segment)`

为 provider network 保留一个 flat 类型的记录

### `def allocate_tenant_segment(self, session)`

```
    def allocate_tenant_segment(self, session):
        # Tenant flat networks are not supported.
        return
```

### `def release_segment(self, session, segment)`

删除创建的 flat 网络的记录

### `def get_mtu(self, physical_network)`

获取 flat network 的 mtu