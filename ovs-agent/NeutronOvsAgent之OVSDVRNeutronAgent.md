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

`registered_dvr_macs` 记录着所有其他 agent 的 dvr记录

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

neutron-server 收到 RPC 消息后回先查询数据库（`DistributedVirtualRouterMacAddress`） 若是数据库内有关于此 host 的记录，则直接返回。
若是没有记录则会创建一个记录（自动生成 mac 地址），同时通知所有的 l2 agent，dvr 有更新（通过 `DVRAgentRpcApiMixin.dvr_mac_address_update`）。即会调用 l2 agent 的 `DVRAgentRpcCallbackMixin.dvr_mac_address_update` 方法。

### `def in_distributed_mode(self)`

```
    def in_distributed_mode(self):
        return self.dvr_mac_address is not None
```

### `def setup_dvr_flows(self)`

支持 dvr 的情况下，初始化相关的流表

1. 调用 `setup_dvr_flows_on_integ_br`  初始化 br-int 相关的流表
2. 调用 `setup_dvr_flows_on_tun_br` 初始化 br-tun 相关的流表
3. 调用 `setup_dvr_flows_on_phys_br` 初始化 br-ex 相关的流表
4. 调用 `setup_dvr_mac_flows_on_all_brs` 设置与各个节点 dvr_mac 相关的流表








### `def setup_dvr_flows_on_integ_br(self)`

1. 若是 `drop_flows_on_start` 为 True，则删除 br-int 上的流表
2. 调用 `int_br.setup_canary_table` 设定如下 flow entity
 1. `cookie=0xa6c90e14ac05d6c1, duration=62937.258s, table=23, n_packets=0, n_bytes=0, idle_age=62937, priority=0 actions=drop`
3. 调用 `int_br.install_drop` 创建如下 flow entity
 1. `cookie=0xa6c90e14ac05d6c1, duration=63037.347s, table=1, n_packets=0, n_bytes=0, idle_age=63037, priority=1 actions=drop`
 2. `cookie=0xa6c90e14ac05d6c1, duration=63132.202s, table=2, n_packets=0, n_bytes=0, idle_age=63132, priority=1 actions=drop`
4. 调用 `int_br.install_normal` 创建如下 flow entity
 1. `cookie=0xa6c90e14ac05d6c1, duration=63211.645s, table=0, n_packets=987, n_bytes=116088, idle_age=12, priority=1 actions=NORMAL`
 2. `cookie=0xa6c90e14ac05d6c1, duration=63211.642s, table=0, n_packets=0, n_bytes=0, idle_age=63211, priority=2,in_port=1 actions=drop`

### `def setup_dvr_flows_on_tun_br(self)`

若是不支持 tunnel network 则直接返回。

1. 调用 `tun_br.install_goto` 创建如下 flow entity
 1. `cookie=0xae728b2a3d3d4b7f, duration=64180.776s, table=0, n_packets=998, n_bytes=117004, idle_age=14, priority=1,in_port=1 actions=resubmit(,1)`
 2. `cookie=0xae728b2a3d3d4b7f, duration=64216.852s, table=9, n_packets=0, n_bytes=0, idle_age=64216, priority=0 actions=resubmit(,10)`
 3. `cookie=0xae728b2a3d3d4b7f, duration=64249.998s, table=1, n_packets=998, n_bytes=117004, idle_age=84, priority=0 actions=resubmit(,2)`

### `def setup_dvr_flows_on_phys_br(self)`

1. 调用 `phys_brs[physical_network].install_goto` 创建如下 flow entity
 1. `cookie=0xa28c2957422125a6, duration=76412.885s, table=0, n_packets=1188, n_bytes=139728, idle_age=36, hard_age=65534, priority=2,in_port=1 actions=resubmit(,1)`
 2. `cookie=0xa28c2957422125a6, duration=76412.880s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1 actions=resubmit(,3)`
2. 调用 `phys_brs[physical_network].install_drop` 创建如下 flow entity
 1. `cookie=0xa28c2957422125a6, duration=76691.832s, table=2, n_packets=1191, n_bytes=140138, idle_age=21, hard_age=65534, priority=2,in_port=1 actions=drop`
3. 调用 `phys_brs[physical_network].install_normal` 创建如下 flow entity
 1. `cookie=0xa28c2957422125a6, duration=76769.202s, table=3, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1 actions=NORMAL`

### `def setup_dvr_mac_flows_on_all_brs(self)`

1. 通过 RPC 获取所有的物理节点的 dvr_mac 列表
2. 去了本节点的 dvr_mac之外，其余的全都调用 `_add_dvr_mac` 方法

### `def _add_dvr_mac(self, mac)`

1. 对于每一个 physical network 都会调用 `_add_dvr_mac_for_phys_br` 方法
2. 若是支持 tunnel network 则会调用 `_add_dvr_mac_for_tun_br` 方法

### `def _add_dvr_mac_for_phys_br(self, physical_network, mac)`

* dvr mac 与 host 的对应关系如下：

```
MariaDB [neutron]> select * from dvr_host_macs;
+-------+-------------------+
| host  | mac_address       |
+-------+-------------------+
| node3 | fa:16:3f:24:77:e3 |
| node2 | fa:16:3f:4d:40:29 |
| node1 | fa:16:3f:cb:84:46 |
+-------+-------------------+
```

1. 调用 `int_br.add_dvr_mac_vlan` 增加如下 flow entity
 * `cookie=0xb003214d22e10131, duration=32624.674s, table=0, n_packets=0, n_bytes=0, idle_age=32624, priority=4,in_port=1,dl_src=fa:16:3f:4d:40:29 actions=resubmit(,2)`
2. 调用 `phys_br.add_dvr_mac_vlan` 增加如下 flow entity
 * `cookie=0xa48e621bd30e85e9, duration=32770.783s, table=3, n_packets=0, n_bytes=0, idle_age=32770, priority=2,dl_src=fa:16:3f:4d:40:29 actions=output:1`

### `def dvr_mac_address_update(self, dvr_macs)`

l2 agent 接收到 dvr 数据库的更新。 dvr_macs 包含数据库中（`dvr_host_macs`）所有的记录

1. 通过与 `registered_dvr_macs` 对比，提取增加和删除的 dvr 记录
2. 对于被删除的 dvr 记录，调用 `_remove_dvr_mac` 方法删除该 agent 上所有关于该 dvr mac 的 flow entity
3. 对于增加的 dvr 记录，调用 `_add_dvr_mac` 方法

### `def _remove_dvr_mac(self, mac)`

1. 调用 `_remove_dvr_mac_for_phys_br` 删除 br-int 和 br-ex 上关于此 dvr mac 的记录
2. 如果启用了 tunnel network 则调用 `_remove_dvr_mac_for_tun_br` 删除该 dvr mac 在与 tunnel network 有关的流表
3. 删除在 `registered_dvr_macs` 保存的 dvr mac 记录

### `def _remove_dvr_mac_for_phys_br(self, physical_network, mac)`

1. 调用 `int_br.remove_dvr_mac_vlan` 删除 br-int 上 table 中关于此 dvr mac 的记录
2. 调用 `phys_br.remove_dvr_mac_vlan` 删除 br-ex 上 table 3 中关于此 dvr mac 的记录

### `def _remove_dvr_mac_for_tun_br(self, mac)`

1. 调用 `int_br.remove_dvr_mac_tun` 删除 br-int table 1 中关于 patch-tun 以及 dvr mac 相关的 flow entity
2. 调用 `tun_br.remove_dvr_mac_tun` 删除 br-tun table 20 中关于 dvr mac 的 flow entity

### `def _add_dvr_mac(self, mac)`

1. 调用 `_add_dvr_mac_for_phys_br` 在 br-ex 和 br-int 上增加该 dvr mac 的记录
2. 若支持 tunnel network，则调用 `_add_dvr_mac_for_tun_br` 在 br-int 、 br-tun 上增加处理东西向流量的 flow entity
3. 在 `registered_dvr_macs` 属性中增加该 dvr mac 的记录


### `def _add_dvr_mac_for_phys_br(self, physical_network, mac)`

1. 调用 `int_br.add_dvr_mac_vlan` 在 br-int 中增加该 dvr mac 的记录
2. 调用 `phys_br.add_dvr_mac_vlan` 在 br-ex 上增加该 dvr mac 的记录

### `def _add_dvr_mac_for_tun_br(self, mac)`

1. 调用 `int_br.add_dvr_mac_tun` 在 br-int 上增加利用 dvr mac 处理东西向流量的 flow entity 
2. 调用 `tun_br.add_dvr_mac_tun` 在 br-tun 上增加利用 dvr mac 处理东西向流量的 flow entity

### `def process_tunneled_network(self, network_type, lvid, segmentation_id)`

调用 `tun_br.provision_local_vlan` 方法创建与 lvid 相关的 flow entity.

### `def bind_port_to_dvr(self, port, local_vlan_map, fixed_ips, device_owner)`

1. 若该 device 为：`DEVICE_OWNER_DVR_INTERFACE`，则调用 `_bind_distributed_router_interface_port`


### `def _bind_distributed_router_interface_port(self, port, lvm, fixed_ips, device_owner)`

1. 通过 RPC `plugin_rpc.get_subnet_for_dvr` 调用获取 port 所在子网的详细信息
2. 根据子网的详细信息创建 `LocalDVRSubnetMapping` 实例 ldm，并加入到 `local_dvr_map` 中
3. 调用 RPC `plugin_rpc.get_ports_on_host_by_subnet` 获取在此 host 的该子网的所有 port
4. 通过 `int_br.get_vifs_by_ids` 获得这些 Port 的 vif 描述
5. 在 ldm 中增加这些 vif
6. 在 local_ports 增加这些 vif
7. 调用 `int_br.install_dvr_to_src_mac` 创建如下流表 `cookie=0xb637cdfd05911130, duration=353007.565s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=4,dl_vlan=1,dl_dst=fa:16:3e:5c:9e:2d actions=strip_vlan,mod_dl_src:fa:16:3e:e0:e5:95,output:3`

 





















### `def unbind_port_from_dvr(self, vif_port, local_vlan_map)`





