# Neutron Ovs Agent 之 br_tun

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/br_tun.py*

## `class OVSTunnelBridge(ovs_bridge.OVSAgentBridge, br_dvr_process.OVSDVRProcessMixin)`

*关于 `OVSDVRProcessMixin` 请参考在 *Neutron Ovs Agent 之 br_phys* 中的介绍*

### `def setup_default_table(self, patch_int_ofport, arp_responder_enabled)`

初始化 br-tun 的基本流表



### `def deferred(self)`

```
    def deferred(self):
        return DeferredOVSTunnelBridge(self)
```

```
class DeferredOVSTunnelBridge(ovs_lib.DeferredOVSBridge):
    _METHODS = [
        'install_unicast_to_tun',
        'delete_unicast_to_tun',
        'install_flood_to_tun',
        'delete_flood_to_tun',
        'install_arp_responder',
        'delete_arp_responder',
        'setup_tunnel_port',
        'cleanup_tunnel_port',
    ]

    def __getattr__(self, name):
        if name in self._METHODS:
            m = getattr(self.br, name)
            return functools.partial(m, deferred_br=self)
        return super(DeferredOVSTunnelBridge, self).__getattr__(name)
```









