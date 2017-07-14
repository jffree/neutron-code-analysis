# Neutron ML2 RPC endpoint 之 DhcpRpcCallback

*neutron/api/rpc/handlers/dhcp_rpc.py*

## `class DhcpRpcCallback(object)`

```
    target = oslo_messaging.Target(
        namespace=n_const.RPC_NAMESPACE_DHCP_PLUGIN,
        version='1.6')
```

### `def get_active_networks_info(self, context, **kwargs)`

**作用：**获取所有活动的网络及其子网、端口的相关信息。若是我们开启了 `dhcp_agent_scheduler` extension 和 `segments` service plugin，则会过滤出与指定 host 上 dhcp agent 绑定的 network 及其 subnet、port 的详细信息

1. 调用 `_get_active_networks` 方法获取该 host 上 dhcp agent 可以访问的所有网络的数据
2. 获取这些网络上的所有 port
3. 获取这些网络下所有允许 dhcp 服务的 subnet
4. 获取 segment service 的实例 `seg_plug`
5. 如果当前的 neutron 支持 segment service，则过滤出那些支持该 Host 的 subnet
6. 按照 network id 对 subnet 和 port 进行分类
7. 返回包含了 subnet 和 port 的 network 信息

### `def _group_by_network_id(self, res)`

* `res`：资源数据（subnet 或者 port）。

根据 network id 将资源分配

### `def _get_active_networks(self, context, **kwargs)`

获取所有活动的 networks。若是 core plugin 支持 `dhcp_agent_scheduler` 则只获取指定 host 上与 dhcp agent 绑定的网络。

`network_auto_schedule` 是否允许为 DHCP agent 自动调度网络资源。在 *neutron.conf* 中设定：`network_auto_schedule = true`

1. 获取 core plugin 的实例 plugin
2. 若是 plugin 支持 `dhcp_agent_scheduler` 的扩展
 1. 若是允许自动为 DHCP 服务自动调度网络资源，则调用 `plugin.auto_schedule_networks` （在 `DhcpAgentSchedulerDbMixin` 中定义）将网络与 dhcp agent 自动绑定；
 2. 调用 `plugin.list_active_networks_on_active_dhcp_agent` （同样是在 `DhcpAgentSchedulerDbMixin` 中实现）获取所有与该 dhcp agent 绑定的 network 的数据，并返回
3. 若是 plugin 不支持 `dhcp_agent_scheduler` 则直接获取所有活动的网络来返回