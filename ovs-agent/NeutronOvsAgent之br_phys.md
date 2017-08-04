# Neutron Ovs Agent 之 br_phys



## `class OVSPhysicalBridge(ovs_bridge.OVSAgentBridge, br_dvr_process.OVSDVRProcessMixin)`

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/br_phys.py*

```
    dvr_process_table_id = constants.DVR_PROCESS_VLAN
    dvr_process_next_table_id = constants.LOCAL_VLAN_TRANSLATION
```

### `def setup_default_table(self)`

```
    def setup_default_table(self):
        self.install_normal()
```

写入这么一个 flow entity。

```
cookie=0xbcaaac3d0239a6e4, duration=554.311s, table=0, n_packets=57, n_bytes=7516, idle_age=8292, priority=0 actions=NORMAL
```

### `def add_dvr_mac_vlan(self, mac, port)`

在 table 3 中增加此 dvr mac 的记录

```
cookie=0xa48e621bd30e85e9, duration=327470.414s, table=3, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_src=fa:16:3f:4d:40:29 actions=output:1
```

### `def remove_dvr_mac_vlan(self, mac)`

删除 table 3 中关于此 dvr mac 的记录

```
cookie=0xa48e621bd30e85e9, duration=319478.446s, table=3, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_src=fa:16:3f:4d:40:29 actions=output:1
``` 

### `def add_dvr_mac_vlan(self, mac, port)`

为该 dvr mac 增加一个 flow entity

```
 cookie=0xa02e63c944a0b07b, duration=194272.621s, table=3, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_src=fa:16:3f:24:77:e3 actions=output:1
```








## `class OVSDVRProcessMixin(object)`

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/br_dvr_process.py*



