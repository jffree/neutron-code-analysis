# Neutron L3 Agnet 之 DvrEdgeHaRouter

*neutron/agent/l3/dvr_edge_ha_router.py*

## `class DvrEdgeHaRouter(dvr_edge_router.DvrEdgeRouter, ha_router.HaRouter)`

```
    def __init__(self, agent, host, *args, **kwargs):
        super(DvrEdgeHaRouter, self).__init__(agent, host,
                                              *args, **kwargs)
        self.enable_snat = None
```

### `def ha_namespace(self)`

当有了 snat- namespace 时，ha namespace 与 snat namespace 一致

### `def internal_network_added(self, port)`

1. 调用 `RouterInfo.internal_network_added`
2. 调用 `_set_subnet_arp_info`设定该 port 所在 subnet 的 arp 信息
3. 调用 `_snat_redirect_add_from_port` 为该 port 实现 snat 的转发功能
4. 若该 router 每有 gateway 或者该 router 不是用来提供 snat 服务的，则退出
5. 调用 `get_snat_port_for_internal_port` 获取 snat port
6. 调用 `_plug_ha_router_port` 增加该 port

### `def _is_this_snat_host(self)`

```
    def _is_this_snat_host(self):
        return (self.agent_conf.agent_mode
                == constants.L3_AGENT_MODE_DVR_SNAT)
```

判断该 l3 agent 是否是用来提供 dvr_snat 服务的

### `def _plug_snat_port(self, port)`

1. 调用 `_get_snat_int_device_name` 获取 snat port 的名称
2. 创建 snat port

### `def initialize(self, process_monitor)`

1. 创建 snat- namespace
2. 调用父类的 initialize 完成其他处理

### `def external_gateway_added(self, ex_gw_port, interface_name)`

1. 调用 `DvrEdgeRouter.external_gateway_added` 完成 gateway 的添加
2. 对于所有的 snat port 来说：
 1. 调用 `_get_snat_int_device_name` 获取 snat port 名称
 2. 调用 `_disable_ipv6_addressing_on_interface` 做 ipv6 处理
 3. 记录这些 port 的 vip
3. 调用 `_add_gateway_vip` 记录 gateway 的 vip
4. 调用 `_disable_ipv6_addressing_on_interface` 处理 gateway port 的 ipv6 信息

### `def external_gateway_removed(self, ex_gw_port, interface_name)`

1. 清除所有的 snat port
2. 清除所有 snat port 的 vip 记录
3. 清除 gateway port
4. 清除 gateway port 的 vip 记录

### `def external_gateway_updated(self, ex_gw_port, interface_name)`

调用 `HaRouter.external_gateway_updated` 完成处理

### `def _external_gateway_added(self, ex_gw_port, interface_name, ns_name, preserve_ips)`

```
    def _external_gateway_added(self, ex_gw_port, interface_name,
                                ns_name, preserve_ips):
        self._plug_external_gateway(ex_gw_port, interface_name, ns_name)
```

### `def _dvr_internal_network_removed(self, port)`

1. 调用 `DvrEdgeRouter._dvr_internal_network_removed` 完成 internal network port 的删除
2. 清除该 port 对应的 snat port 的 vip 记录