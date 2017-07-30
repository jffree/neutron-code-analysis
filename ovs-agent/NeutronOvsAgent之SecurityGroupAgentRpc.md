# Neutron Ovs Agent 之 SecurityGroupAgentRpc

*neutron/agent/securitygroups_rpc.py*

```
    def __init__(self, context, plugin_rpc, local_vlan_map=None,
                 defer_refresh_firewall=False, integration_bridge=None):
        self.context = context
        self.plugin_rpc = plugin_rpc
        self.init_firewall(defer_refresh_firewall, integration_bridge)
```

### `def init_firewall(self, defer_refresh_firewall=False, integration_bridge=None)`

1. `firewall_driver`：在配置中默认为 None，这里为 `firewall_driver = neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver`
2. 调用 `_is_valid_driver_combination` 检测 firewall 的配置是否合法
3. 加载 firewall driver
4. 实例化 firewall driver 类为 `firewall`
5. 初始化其他设置











## `def _is_valid_driver_combination()`

检测关于 firewall 的配置是否合法




