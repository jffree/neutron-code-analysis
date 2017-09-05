# Neutron L3 Agent 之 DvrEdgeRouter

*neutron/agent/l3/dvr_router_base.py*

## `class DvrEdgeRouter(dvr_local_router.DvrLocalRouter)`

实现了对 snat- namespace 相关的操作

```
    def __init__(self, agent, host, *args, **kwargs):
        super(DvrEdgeRouter, self).__init__(agent, host, *args, **kwargs)
        self.snat_namespace = dvr_snat_ns.SnatNamespace(
            self.router_id, self.agent_conf, self.driver, self.use_ipv6)
        self.snat_iptables_manager = None
```

### `def external_gateway_added(self, ex_gw_port, interface_name)`

1. 调用 `DvrLocalRouter.external_gateway_added` 完成前期处理
2. 调用 `_is_this_snat_host` 判断当前 host 是否是用来提供 snat 服务的
3. 若当前 host 是用来提供 snat 服务的，则
 1. 调用 `_create_dvr_gateway` 创建 snat- namespace，创建 snat- port，创建 external gateway port
 2. 调用 `RouterInfo.routes_updated` 更新 router 数据中包含的 route 记录
4. 若当前 host 不是用来提供 snat 服务的，但是 snat- namespace 已经存在，则调用 `external_gateway_removed` 删除 external gateway port，删除 snat- namespace

### `def _is_this_snat_host(self)`

判断当前 host 是否是 gateway port 绑定的 host

### `def _create_dvr_gateway(self, ex_gw_port, gw_interface_name)`

1. 调用 `_create_snat_namespace` 创建 snat- namespace
2. 调用 `get_snat_interfaces` 获取提供 snat 服务的 port
3. 调用 `_plug_snat_port` 创建 sg- port
4. 调用 `_external_gateway_added` 创建 gateway port
5. 为 snat- namespace 创建一个 `IptablesManager` 实例
6. 调用 `RouterInfo._initialize_address_scope_iptables` 初始化 address scope 相关的 iptable rule

### `def _create_snat_namespace(self)`

创建 snat- namespace 

### `def _plug_snat_port(self, port)`

1. 调用 `_get_snat_int_device_name` 获取 sg- 设备名
2. 调用 `_internal_network_added` 创建该 port

### `def _get_snat_int_device_name(self, port_id)`

返回提供 snat 服务的 port 名称 sg-

### `def external_gateway_removed(self, ex_gw_port, interface_name)`

1. 调用 `_external_gateway_removed` 删除 external gateway port
2. 删除 snat- namespace

### `def _external_gateway_removed(self, ex_gw_port, interface_name)`

1. 调用 `DvrLocalRouter.external_gateway_removed` 处理
2. 删除 snat- namespace 中的 external gateway port

### `def external_gateway_updated(self, ex_gw_port, interface_name)`

1. 调用 `_is_this_snat_host` 判断当前 host 是否是用来提供 snat 服务的
2. 若不是用来提供 snat 服务的，但是存在 snat- namespace，则调用 `external_gateway_removed` 清除 external gateway port，删除 snat- namespce，然后返回
3. 若是用来提供 snat 服务的，但不存在 snat- namespace，则调用 `external_gateway_added` 增加  snat- namespace、external gateway port、snat port
4. 若是用来提供 snat 服务的，且存在 snat- namespace，则调用 `_external_gateway_added` 增加 gateway port

### `def internal_network_added(self, port)`

1. 调用 `DvrLocalRouter.internal_network_added` 完成前期处理
2. 调用 `_is_this_snat_host` 判断该 host 是否是用来提供 snat 服务的，若不是，则直接退出
3. 调用 `get_snat_port_for_internal_port` 获取 snat port
4. 获取 snat- namespace 的名称
5. 调用 `_get_snat_int_device_name` 获取 snat port 的名称 sg-
6. 调用 `_internal_network_added` 增加该 port

### `def _dvr_internal_network_removed(self, port)`

1. 调用 `DvrLocalRouter._dvr_internal_network_removed` 完成前期处理
2. 若不存在 external gateway port 则直接退出
3. 调用 `get_snat_port_for_internal_port` 获取 snat port，若不存在则直接退出
4. 若该 host 不是用来提供 snat 服务的，则直接退出
5. 删除该 snat port

### `def _handle_router_snat_rules(self, ex_gw_port, interface_name)`

1. 调用 `DvrLocalRouter._handle_router_snat_rules` 完成前期处理
2. 若不存在 external gateway port 则直接退出
3. 若该 host 不是用来提供 snat 服务的，则直接退出
4. 若不存在 snat iptable manger 则直接退出
5. 调用 `_empty_snat_chains` 清空相对的 chain
6. 调用 `_add_snat_rules` 增加相应的 rule

### `def update_routing_table(self, operation, route)`

```
    def update_routing_table(self, operation, route):
        if self.get_ex_gw_port() and self._is_this_snat_host():
            ns_name = self.snat_namespace.name
            # NOTE: For now let us apply the static routes both in SNAT
            # namespace and Router Namespace, to reduce the complexity.
            if self.snat_namespace.exists():
                super(DvrEdgeRouter, self)._update_routing_table(
                    operation, route, namespace=ns_name)
            else:
                LOG.error(_LE("The SNAT namespace %s does not exist for "
                              "the router."), ns_name)
        super(DvrEdgeRouter, self).update_routing_table(operation, route)
```

当存在 snat- namespace 也需要更新 snat- namespace 的 route 记录

### `def delete(self, agent)`

```
    def delete(self, agent):
        super(DvrEdgeRouter, self).delete(agent)
        if self.snat_namespace.exists():
            self.snat_namespace.delete()
```

### `def process_address_scope(self)`

为 snat port 增加 address scope mark/mask

### `def _delete_stale_external_devices(self, interface_name, pd)`

删除 snat- namespace 中 qg- port