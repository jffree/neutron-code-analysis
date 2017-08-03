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

### `def cleanup_tunnel_port(self, port)`

```
    def cleanup_tunnel_port(self, port):
        self.delete_flows(in_port=port)
```

删除该 ofport 上的流表记录

### `def install_flood_to_tun(self, vlan, tun_id, ports)`

处理经过 tunnel port 的广播消息。

```
 cookie=0x8ca031df7a84a666, duration=1178.439s, table=22, n_packets=0, n_bytes=0, idle_age=65534, priority=1,dl_vlan=1 actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:2,output:3
 cookie=0x8ca031df7a84a666, duration=1177.326s, table=22, n_packets=0, n_bytes=0, idle_age=65534, priority=1,dl_vlan=2 actions=strip_vlan,load:0x34->NXM_NX_TUN_ID[],output:2,output:3
```

去掉本地 vlan、增加当前 tunnel network 的 vni id，然后从 tun port 转发出去

### `def _flood_to_tun_match(ofp, ofpp, vlan)`

构造一个 `OFPMatch` 对象