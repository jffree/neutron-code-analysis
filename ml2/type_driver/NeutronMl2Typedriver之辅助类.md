# Neutron Ml2 typedriver 之辅助类

*neutron/plugins/ml2/drivers/helpers.py*

## `class BaseTypeDriver(api.TypeDriver)`

```
    def __init__(self):
        try:
            self.physnet_mtus = utils.parse_mappings(
                cfg.CONF.ml2.physical_network_mtus, unique_values=False
            )
        except Exception as e:
            LOG.error(_LE("Failed to parse physical_network_mtus: %s"), e)
            self.physnet_mtus = []

    def get_mtu(self, physical_network=None):
        return p_utils.get_deployment_physnet_mtu()
```

* 解析配置中的 `physical_network_mtus` （`<physnet>:<mtu val>`）（物理网络及其对应的 mtu）

* `get_mtu` 方法直接返回 `global_physnet_mtu` 的配置值

## `class SegmentTypeDriver(BaseTypeDriver)`

实现了 tunnel id 的分配

```
    def __init__(self, model):
        super(SegmentTypeDriver, self).__init__()
        self.model = model
        self.primary_keys = set(dict(model.__table__.columns))
        self.primary_keys.remove("allocated")
```

1. `model` 代表着 tunnel network id 的使用情况（对于 vxlan 来说，此 model 既是 `VxlanAllocation`）
2. `primary_keys` 代表着 Model 中的主键（对于 vxlan 来说，既是 `VxlanAllocation.vxlan_vni`）


### `def allocate_fully_specified_segment(self, session, **raw_segment)`

申请一个指定的 tunnel id。

* `filters` 包含有 tunnel id 的信息

### `def allocate_partially_specified_segment(self, session, **filters)`

申请一个 tunnel id。

* `filter`：包含一定的过滤信息，但是不是特定的。

根据过滤出来的结果，选一个随机的 tunnel_id

### `def is_partial_segment(self, segment)`

判断 segment 中是否含有精准的 tunnel id 信息，若没有则返回 true，若有的话则返回 false

### `def reserve_provider_segment(self, session, segment)`

根据 segment 中的信息来请求分配一个 tunnel id，并返回该 tunnel network 的信息。

### `def validate_provider_segment(self, segment)`

验证 segment 数据是否合法