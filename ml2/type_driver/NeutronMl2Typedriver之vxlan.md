# Neutron Ml2 typedriver 之 vxlan

*neutron/plugins/ml2/drivers/type_vxlan.py*

## `class VxlanAllocation(model_base.BASEV2)`

数据表，用于记录 vxlan vni id 的使用情况

## `class VxlanEndpoints(model_base.BASEV2)`

数据表，用于记录 Host 与 endpoint 的对应关系

```
MariaDB [neutron]> select * from ml2_vxlan_endpoints;
+----------------+----------+-------+
| ip_address     | udp_port | host  |
+----------------+----------+-------+
| 172.16.100.117 |     4789 | node3 |
| 172.16.100.192 |     4789 | node1 |
| 172.16.100.51  |     4789 | node2 |
+----------------+----------+-------+
```

## `class VxlanTypeDriver(type_tunnel.EndpointTunnelTypeDriver)`

```
    def __init__(self):
        super(VxlanTypeDriver, self).__init__(
            VxlanAllocation, VxlanEndpoints)
```

### `def get_type(self)`

返回 `vxlan`

### `def initialize(self)`

`cfg.CONF.ml2_type_vxlan.vni_ranges` 代表的是有效的 vxlan vni id 的范围，这里是 `1:1000`

*VNI(Vxlan Network identifier)*

调用 `_initialize` 方法（`TunnelTypeDriver`）实现（主要是进行 vxlan vni id range 的同步操作）。

### `def get_endpoints(self)`

调用 `_get_endpoints` （在 `EndpointTunnelTypeDriver` 中实现），通过查询数据库 `VxlanEndpoints` 中的记录，返回 endpoint 的详细信息

### `def add_endpoint(self, ip, host, udp_port=p_const.VXLAN_UDP_PORT)`

调用 `_add_endpoint` 创建一个 `VxlanEndpoints` 数据库记录

### `def get_mtu(self, physical_network=None)`

计算除去 vxlan 封装外可供用户使用的 mtu 长度

[VXLAN学习整理](http://www.aboutyun.com/thread-11189-1-1.html)