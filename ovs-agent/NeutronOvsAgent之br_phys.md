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






## `class OVSDVRProcessMixin(object)`

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/br_dvr_process.py*



