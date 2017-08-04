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

### `def install_arp_responder(self, vlan, ip, mac)`

1. 调用 `_arp_responder_match` 构造一个 `OFMatch` 对象
2. 调用 `install_apply_actions` 创建一个 flow entity

* 实例如下：

```
 cookie=0x8ca031df7a84a666, duration=107668.474s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=1,arp_tpa=192.168.100.2 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163e513bf7->NXM_NX_ARP_SHA[],load:0xc0a86402->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:51:3b:f7,IN_PORT
```

* 解析：
 1. move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[]，表示将ARP Request数据包的源MAC地址作为ARP Reply数据包的目的MAC地址
 2. mod_dl_src:%(mac)s，表示将ARP Request请求的目的虚拟机的MAC地址作为ARP Reply数据包的源MAC地址
 3. load:0x2->NXM_OF_ARP_OP[]，表示将构造的ARP包的类型设置为ARP Reply
 4. move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[]，表示将Request中的源MAC地址作为Reply中的目的MAC地址
 5. move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[]，表示将表示将Request中的源IP地址作为Reply中的目的IP地址
 6. load:%(mac)#x->NXM_NX_ARP_SHA[]，表示将Request请求的目的虚拟机的MAC地址作为Reply中的源MAC地址
 7. load:%(ip)#x->NXM_OF_ARP_SPA[]，表示将表示将Request请求的目的虚拟机的IP地址作为Reply中的源IP地址
 8. inport，表示将封装好ARP Reply从ARP Request的入端口送出，返回给源虚拟机

[OVS流表分析](http://www.sdnlab.com/16414.html)

### `def _arp_responder_match(ofp, ofpp, vlan, ip)`

构造一个 `OFPMatch` 对象（包含 vlan、dl_dst、ip）

### `def delete_arp_responder(self, vlan, ip)`

根据 vlan 和 ip 删除一条 arp response 的流表

### `def install_unicast_to_tun(self, vlan, tun_id, port, mac)`

为目的地址为 mac 指定一条访问 flow entity。

```
 cookie=0x8ca031df7a84a666, duration=108550.333s, table=20, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_vlan=1,dl_dst=fa:16:3e:51:3b:f7 actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:3
```

### `def delete_flood_to_tun(self, vlan)`

删除 22 表中与 vlan 号一致的 flood flow entity。

### `def delete_unicast_to_tun(self, vlan, mac)`

删除 20 表中与 vlan、mac 一致的 unicast flow entity



