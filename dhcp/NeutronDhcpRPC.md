# Neutron dhcp RPC

## `class DhcpPluginApi(object)`

* 这个类是 dhcp agent 的 RPC Client 端。
 1. topic：`q-plugin`
 2. host：`conf.host`
 3. version：`1.0`
* 对应的 RPC Server 端的 endpoint 为：`neutron.api.rpc.handlers.dhcp_rpc.DhcpRpcCallback`，在 `ml2.start_rpc_listeners`
 1. topic：`q-plugin`
 2. fanout：false

```
    def __init__(self, topic, host):
        self.host = host
        target = oslo_messaging.Target(
                topic=topic,
                namespace=n_const.RPC_NAMESPACE_DHCP_PLUGIN,
                version='1.0')
        self.client = n_rpc.get_client(target)
```

### `def context(self)`

属性方法，构造含有 admin 权限的 context

### `def get_active_networks_info(self)`

调用 server 端的 `get_active_networks_info` 方法

### `def get_network_info(self, network_id)`

调用 server 端的 `get_network_info` 方法

### `def create_dhcp_port(self, port)`

调用 server 端的 `create_dhcp_port` 方法

### `def update_dhcp_port(self, port_id, port)`

调用 server 端的 `update_dhcp_port` 方法

### `def release_dhcp_port(self, network_id, device_id)`

调用 server 端的 `release_dhcp_port` 方法

### `def dhcp_ready_on_ports(self, port_ids)`

调用 server 端的 `dhcp_ready_on_ports` 方法

## `class DhcpRpcCallback(object)`

```
    target = oslo_messaging.Target(
        namespace=n_const.RPC_NAMESPACE_DHCP_PLUGIN,
        version='1.6')
```
### `def dhcp_ready_on_ports(self, context, port_ids)`

