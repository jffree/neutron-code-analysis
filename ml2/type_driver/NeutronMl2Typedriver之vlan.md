# Neutron Ml2 type driver 之 vlan

## `class VlanAllocation(model_base.BASEV2)`

vlan id 的使用情况

## `class VlanTypeDriver(helpers.SegmentTypeDriver)`

```
    def __init__(self):
        super(VlanTypeDriver, self).__init__(VlanAllocation)
        self._parse_network_vlan_ranges()
```

调用 `_parse_network_vlan_ranges` 解析 vlan 的配置参数（`<physical_network>:<vlan_min>:<vlan_max>`）。

### `def _parse_network_vlan_ranges(self)`

解析 vlan 的配置信息

例如：`network_vlan_ranges = default:3001:4000`

则会解析成为：`self.network_vlan_ranges = {'default': [(3001, 4000)]}`

### `def get_type(self)`

返回 `vlan`

### `def initialize(self)`

调用 `_sync_vlan_allocations` 将 vlan 的设置信息与数据库记录进行同步

### `def _sync_vlan_allocations(self)`

将 vlan 的设置信息与数据库记录进行同步（neutron-server 重启时可能需要，因为用户有可能修改了 `network_vlan_ranges` 的设置）

### `def is_partial_segment(self, segment)`

判断是否为随机分配。若 segment 数据中不包含 id，则调用认为是随机分配。

### `def validate_provider_segment(self, segment)`

创建 provider network 时，判断 segment 参数是否正确。

创建 vlan 类型的 provider network 时，必须有 `physical_network` 参数。

### `def reserve_provider_segment(self, session, segment)`

为 provider network 保留一个 vlan id。

根据 segment 内数据的不同而分别调用 `allocate_partially_specified_segment` 或者 `allocate_fully_specified_segment` 进行 vlan id 的分配

### `def allocate_tenant_segment(self, session)`

为 tenant network 随机分配一个 vlan id

### `def release_segment(self, session, segment)`

回收 vlan id。

### `def get_mtu(self, physical_network)`

获取该 physical network 的 mtu