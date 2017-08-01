# Neutron Ml2 type driver 之 type_tunnel

*neutron/plugins/ml2/drivers/type_tunnel.py*

为 tunnel network 定义一些公共方法。

tunnel network 共有三类，分别是：vxlan、geneve、gre。我只拿 vxlan 来说明情况

## `class TunnelTypeDriver(helpers.SegmentTypeDriver)`

抽象基类

```
@six.add_metaclass(abc.ABCMeta)
class TunnelTypeDriver(helpers.SegmentTypeDriver):
    """Define stable abstract interface for ML2 type drivers.

    tunnel type networks rely on tunnel endpoints. This class defines abstract
    methods to manage these endpoints.
    """
    BULK_SIZE = 100

    def __init__(self, model):
        super(TunnelTypeDriver, self).__init__(model)
        self.segmentation_key = next(iter(self.primary_keys))
```

`segmentation_key` 代表着 tunnel network id model 主键中的一个

### `def _initialize(self, raw_tunnel_ranges)`

```
    def _initialize(self, raw_tunnel_ranges):
        self.tunnel_ranges = []
        self._parse_tunnel_ranges(raw_tunnel_ranges, self.tunnel_ranges)
        self.sync_allocations()
```

1. 解析 tunnel 的标识范围（例如，对于 vxlan 来说其标识即 VNI）。
2. 调用 `sync_allocations` 同步数据库中的的 tunnel network id range 和 设置中的 tunnel network id rang

### `def sync_allocations(self)`

同步数据库中的的 tunnel network id range 和 设置中的 tunnel network id rang。

例如：

1. neutron-server 第一次启动时 vxlan vni id range 为： 100:800
2. neutron-server 第二次启动时 vxlan vni id range 被设定为 400:1000，这时就需要更新数据库中的记录（将 100-399 删除，将 801-1000 加入）

### `def get_mtu(self, physical_network=None)`

`overlay_ip_version` 是指 overlay/tunnel network 的 ip 版本

1. 首先获取 `global_physnet_mtu` 的设定值，默认为 1500
2. 若用户设定了 `path_mtu` 也获取这个值，选择 `path_mtu` 与 `global_physnet_mtu` 中的较小值作为起始的 mtu 大小
3. 用起始 mtu 减去外部封装的 ip 头部的长度（20）
4. 后面还需要根据具体的网络类型进行进一步的计算

### `def get_allocation(self, session, tunnel_id)`

获取 tunnel_id 数据库记录

### `def release_segment(self, session, segment)`

* 释放之前被申请的 tunnel_id，这里有两种情况：
 1. tunnel_id 在 tunnel_ranges 之内，则将其在 model 内的记录置为 false（未使用）
 2. tunnel_id 不在 tunnel_ranges 之内，则将其在 model 内的记录直接删除

### `def allocate_tenant_segment(self, session)`

调用 `allocate_partially_specified_segment` （`SegmentTypeDriver` 中实现）分配一个随机的 tunnel id

## `class EndpointTunnelTypeDriver(TunnelTypeDriver)`

封装了对 endpint model（例如 vxlan 的 `VxlanEndpoints`）操作的封装

```
    def __init__(self, segment_model, endpoint_model):
        super(EndpointTunnelTypeDriver, self).__init__(segment_model)
        self.endpoint_model = endpoint_model
        self.segmentation_key = next(iter(self.primary_keys))
```

### `def _get_endpoints(self)`

```
    def _get_endpoints(self):
        LOG.debug("_get_endpoints() called")
        session = db_api.get_session()
        return session.query(self.endpoint_model)
```

查询 endpoint_model 数据库（对于 vxlan 来说，此数据库既是：`VxlanEndpoints`）

### `def _add_endpoint(self, ip, host, **kwargs)`

创建一个 endpoint_model 数据库记录

### `def get_endpoint_by_host(self, host)`

根据 host 查询 endpoint_model 的数据库记录

### `def get_endpoint_by_ip(self, ip)`

根据 ip 查询 endpoint_model 数据库的记录

### `def delete_endpoint(self, ip)`

根据 ip 删除 endpoint_model 数据库记录

### `def delete_endpoint_by_host_or_ip(self, host, ip)`

根据 ip 或者 host （两者有一个符合即可）删除 endpoint model 数据库记录