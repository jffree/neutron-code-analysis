# Neutron ML2 RPC endpoint 之 DhcpRpcCallback

*neutron/api/rpc/handlers/dhcp_rpc.py*

## `class DhcpRpcCallback(object)`

```
    target = oslo_messaging.Target(
        namespace=n_const.RPC_NAMESPACE_DHCP_PLUGIN,
        version='1.6')
```

### `def get_active_networks_info(self, context, **kwargs)`

1. 调用 `_get_active_networks` 方法获取该 host 上 dhcp agent 可以访问的所有网络的数据
2. 获取这些网络上的所有 port
3. 获取这些网络下所有允许 dhcp 服务的子网
4. 获取 segment service 的实例 `seg_plug`
5. 如果当前的 neutron 支持 segment service 并且存在设有 `segment_id` 的子网：

**unfinished**













### `def _get_active_networks(self, context, **kwargs)`

`network_auto_schedule` 是否允许为 DHCP agent 自动调度网络资源。在 *neutron.conf* 中设定：`network_auto_schedule = true`

1. 获取 core plugin 的实例 plugin
2. 若是 plugin 支持 `dhcp_agent_scheduler` 的扩展
 1. 若是允许自动为 DHCP 服务自动调度网络资源，则调用 `plugin.auto_schedule_networks` （在 `DhcpAgentSchedulerDbMixin` 中定义）将网络与 dhcp agent 自动绑定；
 2. 调用 `plugin.list_active_networks_on_active_dhcp_agent` （同样是在 `DhcpAgentSchedulerDbMixin` 中实现）获取所有与该 dhcp agent 绑定的 network 的数据，并返回
3. 若是 plugin 不支持 `dhcp_agent_scheduler` 则直接获取所有活动的网络来返回