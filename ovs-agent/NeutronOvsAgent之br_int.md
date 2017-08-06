# Neutron Ovs Agent 之 br_int

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/br_int.py*

## `class OVSIntegrationBridge(ovs_bridge.OVSAgentBridge)`

### `def setup_default_table(self)`

1. 调用 `setup_canary_table` 在表 23 的增加一个优先级为 0，动作为 drop 的 entity。
2. 调用 `install_normal` 在表 0 中增加一个优先级为 0，动作为 normal 的 entity。
 * `ovs-ofctl dump-flows br-int table=0`
 * `cookie=0x8ced2ffea2e42db3, duration=86000.044s, table=0, n_packets=13696, n_bytes=1610888, idle_age=49, hard_age=65534, priority=0 actions=NORMAL` 
3. 调用 `install_drop` 在表 24 中增加一个优先级为 0 动作为 drop 的 entity
 * `ovs-ofctl dump-flows br-int table=24`
 * `cookie=0x8ced2ffea2e42db3, duration=86362.812s, table=24, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=0 actions=drop` 

### `def setup_canary_table(self)`

```
    def setup_canary_table(self):
        self.install_drop(constants.CANARY_TABLE)
```

在表 23 的增加采取 drop 动作 entity。

`ovs-ofctl dump-flows br-int table=23`

```
NXST_FLOW reply (xid=0x4):
 cookie=0x8ced2ffea2e42db3, duration=85865.318s, table=23, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=0 actions=drop
```

### `def check_canary_table(self)`

检查 br-int 中 openflow 23 号表是否存在流表。若存在则返回 `OVS_NORMAL`，不存在则返回 `OVS_RESTARTED`。

### `def _local_vlan_match(_ofp, ofpp, port, vlan_vid)`

```
    @staticmethod
    def _local_vlan_match(_ofp, ofpp, port, vlan_vid):
        return ofpp.OFPMatch(in_port=port, vlan_vid=vlan_vid)
```

构造一个 `OFMatch` 对象

### `def provision_local_vlan(self, port, lvid, segmentation_id)`

根据 segmentation_id 来限定外部来的网络那些可以转发到 lvid 代表的 Network port 上

```
cookie=0xb637cdfd05911130, duration=351157.550s, table=0, n_packets=946, n_bytes=90471, idle_age=65534, hard_age=65534, priority=3,in_port=1,vlan_tci=0x0000/0x1fff actions=mod_vlan_vid:3,NORMAL
```

### `def add_dvr_mac_vlan(self, mac, port)`

生成一下 flow entity

`cookie=0xb003214d22e10131, duration=32624.674s, table=0, n_packets=0, n_bytes=0, idle_age=32624, priority=4,in_port=1,dl_src=fa:16:3f:4d:40:29 actions=resubmit(,2)`

### `def remove_dvr_mac_vlan(self, mac)`

调用 `delete_flows` 删除关于 table 1 中 dvr mac 的记录

```
 cookie=0xb637cdfd05911130, duration=189898.048s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=4,in_port=1,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,2)
 cookie=0xb637cdfd05911130, duration=189898.044s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=7,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,1)
```

### `def remove_dvr_mac_tun(self, mac, port)`

调用 `delete_flows` 删除 table 1 中从 patch-tun-pot 以及 dvr mac 的记录

```
 cookie=0xb637cdfd05911130, duration=189898.044s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=7,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,1)
```

**疑问：**是否 `remove_dvr_mac_vlan` 已经全部删除了 table 1 中所有与 dvr mac 相关的 flow entity？

### `def add_dvr_mac_vlan(self, mac, port)`

调用 `install_goto` 为该 dvr mac 在 table 0 创建一个 flow entity

```
 cookie=0xb637cdfd05911130, duration=194105.131s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=4,in_port=1,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,2)
```

### `def add_dvr_mac_tun(self, mac, port)`

在 br-int 上利用 dvr mac 增加处理东西向流量的 flow entity

```
 cookie=0xb637cdfd05911130, duration=194580.738s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=7,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,1)
```

### `def delete_arp_spoofing_protection(self, port)`

1. 调用 `_arp_reply_match` 构造好 OFPMatch，然后调用 `delete_flows` 删除与该 port arp 有关的 flow entity
2. 调用 `_icmpv6_reply_match` 构造好 OFPMatch，然后调用 `delete_flows` 删除与该 port icmpv6 有关的 flow entity
3. 调用 `delete_arp_spoofing_allow_rules` 删除 table 24 中关于该 port arp responser 转发的记录

### `def _arp_reply_match(ofp, ofpp, port)`

构造一个 OFPMatch

### `def delete_arp_spoofing_allow_rules(self, port)`

删除 table 24 中关于该 port arp responser 的记录

### `def install_dvr_to_src_mac(self, network_type, vlan_tag, gateway_mac, dst_mac, dst_port)`

1. 调用 `_dvr_to_src_mac_table_id` 根据 network type 获取需要设定的表格

```
cookie=0xb637cdfd05911130, duration=353007.565s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=4,dl_vlan=1,dl_dst=fa:16:3e:5c:9e:2d actions=strip_vlan,mod_dl_src:fa:16:3e:e0:e5:95,output:3
```













