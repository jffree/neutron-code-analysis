# Neutron Ovs Agent RPC 之 DVRServerRpcApi

* `DVRServerRpcApi` 为 Neutron Ovs Agent RPC Client
 1. topic：`q-plugin`
 2. version：`1.0`
* RPC Server 端在 `ml2.start_rpc_listeners` 完成初始化
 * endpoint：`DVRServerRpcCallback`

这个 RPC Client 和 RPC Server 在同一个模块内

*neutron/api/rpc/handlers/dvr_rpc.py*

## `class DVRServerRpcApi(object)`

```
    def __init__(self, topic):
        target = oslo_messaging.Target(topic=topic, version='1.0',
                                       namespace=constants.RPC_NAMESPACE_DVR)
        self.client = n_rpc.get_client(target)
```

### `def get_dvr_mac_address_by_host(self, context, host)`

调用 Server 端的 `get_dvr_mac_address_by_host` 方法

### `def get_dvr_mac_address_list(self, context)`

调用 Server 端的 `get_dvr_mac_address_list` 方法

### `def get_ports_on_host_by_subnet(self, context, host, subnet)`

调用 Server 端的 `get_ports_on_host_by_subnet` 方法

### `def get_subnet_for_dvr(self, context, subnet, fixed_ips)`

调用 Server 端的 `get_subnet_for_dvr` 方法

## `class DVRServerRpcCallback(object)`

```
    target = oslo_messaging.Target(version='1.1',
                                   namespace=constants.RPC_NAMESPACE_DVR)
```

### `def plugin(self)`

属性方法，获取 core plugin 的实例

### `def get_dvr_mac_address_list(self, context)`


### `def get_dvr_mac_address_by_host(self, context, **kwargs)`


### `def get_ports_on_host_by_subnet(self, context, **kwargs)`


### `def get_subnet_for_dvr(self, context, **kwargs)`



















