# Neutron Ovs Agent 之 OVSDVRNeutronAgent

*neutron/plugins/ml2/drivers/openvswitch/agent/ovs_dvr_neutron_agent.py*

## `class OVSDVRNeutronAgent(object)`

```
    def __init__(self, context, plugin_rpc, integ_br, tun_br,
                 bridge_mappings, phys_brs, int_ofports, phys_ofports,
                 patch_int_ofport=constants.OFPORT_INVALID,
                 patch_tun_ofport=constants.OFPORT_INVALID,
                 host=None, enable_tunneling=False,
                 enable_distributed_routing=False):
        self.context = context
        self.plugin_rpc = plugin_rpc
        self.host = host
        self.enable_tunneling = enable_tunneling
        self.enable_distributed_routing = enable_distributed_routing
        self.bridge_mappings = bridge_mappings
        self.phys_brs = phys_brs
        self.int_ofports = int_ofports
        self.phys_ofports = phys_ofports
        self.reset_ovs_parameters(integ_br, tun_br,
                                  patch_int_ofport, patch_tun_ofport)
        self.reset_dvr_parameters()
        self.dvr_mac_address = None
        if self.enable_distributed_routing:
            self.get_dvr_mac_address()
        self.conf = cfg.CONF
```

1. `context` admin 权限的 conetxt
2. `plugin_rpc`：`DVRServerRpcApi` 实例（RPC Client），用于和 neutron-server 进行 RPC 通信
3. `host` 所在主机的名称
4. `enable_tunneling`：是否支持 tunnel 网络
5. `enable_distributed_routing` 是否使用 DVR 模式
6. `bridge_mappings`：配置选项（<physical_network>:<physical_bridge>）
7. `phys_brs`: physical bridge 实例（br-ex）
8. `int_ofports` 用于和 physical bridge 连接的位于 br-int port （int-br-ex）的 ofport
9. `phys_ofports`：用于和 br-int 连接的位于 br-ex 上的 port （phy-br-ex）的 ofport
10. 调用 `reset_ovs_parameters` 设定一些属性
11. 调用 `reset_dvr_parameters` 初始化一些属性
12. 若 `enable_distributed_routing` 为真，则调用 `get_dvr_mac_address`

### `def reset_ovs_parameters(self, integ_br, tun_br, patch_int_ofport, patch_tun_ofport)`

```
    def reset_ovs_parameters(self, integ_br, tun_br,
                             patch_int_ofport, patch_tun_ofport):
        '''Reset the openvswitch parameters'''
        self.int_br = integ_br
        self.tun_br = tun_br
        self.patch_int_ofport = patch_int_ofport
        self.patch_tun_ofport = patch_tun_ofport
```

### `def reset_dvr_parameters(self)`

```
    def reset_dvr_parameters(self):
        '''Reset the DVR parameters'''
        self.local_dvr_map = {}
        self.local_csnat_map = {}
        self.local_ports = {}
        self.registered_dvr_macs = set()
```

### `def get_dvr_mac_address(self)`

调用 `get_dvr_mac_address_with_retry`

### `def get_dvr_mac_address_with_retry(self)`

通过 RPC 调用 Server 端的 `get_dvr_mac_address_by_host` 方法（获取该 host 上的 dvr mac 地址）

```
MariaDB [neutron]> select * from dvr_host_macs;
+----------+-------------------+
| host     | mac_address       |
+----------+-------------------+
| CentOS-7 | fa:16:3f:59:e6:f6 |
+----------+-------------------+
```

### `def in_distributed_mode(self)`

```
    def in_distributed_mode(self):
        return self.dvr_mac_address is not None
```

### `def setup_dvr_flows(self)`

支持 dvr 的情况下，初始化相关的流表














