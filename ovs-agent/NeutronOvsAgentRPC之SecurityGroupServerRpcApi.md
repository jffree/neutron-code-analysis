# Neutron Ovs Agent RPC 之 SecurityGroupServerRpcApi

* `SecurityGroupServerRpcApi` 为 Neutron Ovs Agent RPC Client
 1. topic：`q-plugin`
 2. version：`1.0`
* RPC Server 端在 `ml2.start_rpc_listeners` 完成初始化
 * endpoint：`SecurityGroupServerRpcCallback`

这个 RPC Client 和 RPC Server 在同一个模块内


*neutron/agent/securitygroups_rpc.py*

```
SecurityGroupServerRpcApi = (
    securitygroups_rpc.SecurityGroupServerRpcApi
)
```

## `class SecurityGroupServerRpcApi(object)`

*neutron/api/rpc/handlers/securitygroups_rpc.py*

```
    def __init__(self, topic):
        target = oslo_messaging.Target(
            topic=topic, version='1.0',
            namespace=constants.RPC_NAMESPACE_SECGROUP)
        self.client = n_rpc.get_client(target)
```

### `def security_group_rules_for_devices(self, context, devices)`

调用  Server 端的 `security_group_rules_for_devices` 方法

### `def security_group_info_for_devices(self, context, devices)`

调用 Server 端的 `security_group_info_for_devices` 方法

## `class SecurityGroupServerRpcCallback(object)`

```
    target = oslo_messaging.Target(version='1.2',
                                   namespace=constants.RPC_NAMESPACE_SECGROUP)
```

### `def plugin(self)`

属性方法，获取 core plugin 实例

### `def _get_devices_info(self, context, devices)`



### `def security_group_rules_for_devices(self, context, **kwargs)`


### `def security_group_info_for_devices(self, context, **kwargs)`



