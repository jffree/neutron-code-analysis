# Neutron L3 Agent 之 Ha AgentMixin

*neutron/agent/l3/dvr.py*

## `class AgentMixin(object)`

```
class AgentMixin(object):
    def __init__(self, host):
        # dvr data
        self._fip_namespaces = weakref.WeakValueDictionary()
        super(AgentMixin, self).__init__(host)
```

### `def get_fip_ns(self, ext_net_id)`

1. 根据 external network id，判断当前的 l3 agent 是否已经存在其 fip- namespace，若有则直接返回
2. 若没有，则构造一个 `FipNamespace` 实例

### `def get_ports_by_subnet(self, subnet_id)`

通过 RPC 获取该 subnet 上的 port

### `def add_arp_entry(self, context, payload)`

```
    def add_arp_entry(self, context, payload):
        """Add arp entry into router namespace.  Called from RPC."""
        self._update_arp_entry(context, payload, 'add')
```

### `def del_arp_entry(self, context, payload)`

```
    def del_arp_entry(self, context, payload):
        """Delete arp entry from router namespace.  Called from RPC."""
        self._update_arp_entry(context, payload, 'delete')
```

### `def _update_arp_entry(self, context, payload, action)`

调用 router info 的 `_update_arp_entry` 完成 arp 记录的更新

```
[root@node1 ~]# ip netns exec qrouter-61eaacf9-d4e0-4202-bac9-321da0ceaa69 arp -n
```

### `def fipnamespace_delete_on_ext_net(self, context, ext_net_id)`

当 external network 从该 host 被移除（没有与之相关的 port）时，则删除其 fip- namespace