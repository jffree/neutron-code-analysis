# Neutron Ml2 RPC endpoints 之 RpcCallbacks

## `class TunnelRpcCallbackMixin(object)`

### `def setup_tunnel_callback_mixin(self, notifier, type_manager)`

```
    def setup_tunnel_callback_mixin(self, notifier, type_manager):
        self._notifier = notifier
        self._type_manager = type_manager
```

### `def tunnel_sync(self, rpc_context, **kwargs)`



## `class RpcCallbacks(type_tunnel.TunnelRpcCallbackMixin)`

```
    target = oslo_messaging.Target(version='1.5')
```

target 指明了这个 endpoint 的版本

### `__init__` 方法

```
    def __init__(self, notifier, type_manager):
        self.setup_tunnel_callback_mixin(notifier, type_manager)
        super(RpcCallbacks, self).__init__()
```

`setup_tunnel_callback_mixin` 在 `TunnelRpcCallbackMixin` 中定义，定义了 `_notifier` 和 `_type_manager` 两个实例变量。

### ``