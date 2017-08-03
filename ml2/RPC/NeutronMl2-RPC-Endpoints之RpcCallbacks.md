# Neutron Ml2 RPC endpoints 之 RpcCallbacks

## `class TunnelRpcCallbackMixin(object)`

### `def setup_tunnel_callback_mixin(self, notifier, type_manager)`

```
    def setup_tunnel_callback_mixin(self, notifier, type_manager):
        self._notifier = notifier
        self._type_manager = type_manager
```

### `def tunnel_sync(self, rpc_context, **kwargs)`

1. 检验 `tunnel_ip`、`host`、`tunnel_type` 参数的正确性。
2. 根据 tunnel_type，获取其对应的 ml2 type driver 实例（我们这里是 vxlan）
3. 调用 type driver 的 `get_endpoint_by_host` 获取 endpoint 数据库的记录
4. 调用 type driver 的 `get_endpoint_by_ip` 获取 endpoint 数据库的记录
5. 根据最先传递过来的 tunnel_ip 和 host 的对应关系，检查数据库中存储的数据是否有不一致的情况，若有不一致的情况则删除该记录，其中若是 endpoint 的 ip 发生了变化的话，则调用 `_notifier.tunnel_delete`（`TunnelAgentRpcApiMixin` 实现） 发送 RPC 消息到各个 l2 agent，告诉各个 l2 agent 有 endpoint 记录删除。
6. 为该 host 与 tunnel_ip 的对应关系增加一个新的 endpoint 记录
7. 调用 type driver 的 `get_endpoints` 获取当前所有的 endpoint 的数据库记录
8. 调用 `_notifier.tunnel_update` （`TunnelAgentRpcApiMixin` 实现）发送 RPC 消息到所有 l2 agent，通知当前 endpoint 的数据

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