# Neutron Ovs Agent RPC 之 OVSPluginApi

* `OVSPluginApi` 为 Neutron Ovs Agent RPC Client
 1. topic：`q-plugin`
 2. version：`1.0`
* RPC Server 端在 `ml2.start_rpc_listeners` 完成初始化
 * endpoint：`RpcCallbacks`

## `class OVSPluginApi(agent_rpc.PluginApi)`

*neutron/plugins/ml2/drivers/openvswitch/agent/ovs_neutron_agent.py*

```
class OVSPluginApi(agent_rpc.PluginApi):
    pass
```

## `class PluginApi(object)`

*neutron/agent/rpc.py*

```
    def __init__(self, topic):
        target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(target)
```

### `def get_device_details(self, context, device, agent_id, host=None)`

调用 Server 端的 `get_device_details` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `RpcCallbacks` 中实现）

### `def get_devices_details_list(self, context, devices, agent_id, host=None)`

调用 Server 端的 `get_devices_details_list` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `RpcCallbacks` 中实现）

### `def get_devices_details_list_and_failed_devices(self, context, devices, agent_id, host=None)`

调用 Server 端的 `get_devices_details_list_and_failed_devices` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `RpcCallbacks` 中实现）

### `def update_device_down(self, context, device, agent_id, host=None)`

调用 Server 端的 `update_device_down` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `RpcCallbacks` 中实现）

### `def update_device_up(self, context, device, agent_id, host=None)`

调用 Server 端的 `update_device_up` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `RpcCallbacks` 中实现）

### `def _device_list_rpc_call_with_failed_dev(self, rpc_call, context, agent_id, host, devices)`

通过 `rpc_call` 方法获取失效和激活的 device

### `def update_device_list(self, context, devices_up, devices_down, agent_id, host)`

调用 Server 端的 `update_device_list` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `RpcCallbacks` 中实现）

### `def tunnel_sync(self, context, tunnel_ip, tunnel_type=None, host=None)`

调用 Server 端的 `tunnel_sync` 方法。（在 *neutron/plugins/ml2/rpc.py* 的 `TunnelRpcCallbackMixin` 中（`RpcCallbacks` 的父类）实现）