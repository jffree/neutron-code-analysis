# Neutron Ovs Agent 之 OVSNeutronAgent

*neutron/plugins/ml2/drivers/openvswitch/agent/ovs_neutron_agent.py*

## `class OVSNeutronAgent`

```
@profiler.trace_cls("rpc")
class OVSNeutronAgent(sg_rpc.SecurityGroupAgentRpcCallbackMixin,
                      l2population_rpc.L2populationRpcCallBackTunnelMixin,
                      dvr_rpc.DVRAgentRpcCallbackMixin):
    '''Implements OVS-based tunneling, VLANs and flat networks.

    Two local bridges are created: an integration bridge (defaults to
    'br-int') and a tunneling bridge (defaults to 'br-tun'). An
    additional bridge is created for each physical network interface
    used for VLANs and/or flat networks.

    All VM VIFs are plugged into the integration bridge. VM VIFs on a
    given virtual network share a common "local" VLAN (i.e. not
    propagated externally). The VLAN id of this local VLAN is mapped
    to the physical networking details realizing that virtual network.

    For virtual networks realized as GRE tunnels, a Logical Switch
    (LS) identifier is used to differentiate tenant traffic on
    inter-HV tunnels. A mesh of tunnels is created to other
    Hypervisors in the cloud. These tunnels originate and terminate on
    the tunneling bridge of each hypervisor. Port patching is done to
    connect local VLANs on the integration bridge to inter-hypervisor
    tunnels on the tunnel bridge.

    For each virtual network realized as a VLAN or flat network, a
    veth or a pair of patch ports is used to connect the local VLAN on
    the integration bridge with the physical network bridge, with flow
    rules adding, modifying, or stripping VLAN tags as necessary.
    '''

    # history
    #   1.0 Initial version
    #   1.1 Support Security Group RPC
    #   1.2 Support DVR (Distributed Virtual Router) RPC
    #   1.3 Added param devices_to_update to security_groups_provider_updated
    #   1.4 Added support for network_update
    target = oslo_messaging.Target(version='1.4')

    def __init__(self, bridge_classes, conf=None):
        '''Constructor.

        :param bridge_classes: a dict for bridge classes.
        :param conf: an instance of ConfigOpts
        '''
        super(OVSNeutronAgent, self).__init__()
        self.conf = conf or cfg.CONF
        self.ovs = ovs_lib.BaseOVS()
        agent_conf = self.conf.AGENT
        ovs_conf = self.conf.OVS

        self.fullsync = False
        # init bridge classes with configured datapath type.
        self.br_int_cls, self.br_phys_cls, self.br_tun_cls = (
            functools.partial(bridge_classes[b],
                              datapath_type=ovs_conf.datapath_type)
            for b in ('br_int', 'br_phys', 'br_tun'))

        self.use_veth_interconnection = ovs_conf.use_veth_interconnection
        self.veth_mtu = agent_conf.veth_mtu
        self.available_local_vlans = set(moves.range(p_const.MIN_VLAN_TAG,
                                                     p_const.MAX_VLAN_TAG))
        self.tunnel_types = agent_conf.tunnel_types or []
        self.l2_pop = agent_conf.l2_population
        # TODO(ethuleau): Change ARP responder so it's not dependent on the
        #                 ML2 l2 population mechanism driver.
        self.enable_distributed_routing = agent_conf.enable_distributed_routing
        self.arp_responder_enabled = agent_conf.arp_responder and self.l2_pop

        host = self.conf.host
        self.agent_id = 'ovs-agent-%s' % host

        self.enable_tunneling = bool(self.tunnel_types)

        # Validate agent configurations
        self._check_agent_configurations()

        # Keep track of int_br's device count for use by _report_state()
        self.int_br_device_count = 0

        self.int_br = self.br_int_cls(ovs_conf.integration_bridge)
        self.setup_integration_br()
        # Stores port update notifications for processing in main rpc loop
        self.updated_ports = set()
        # Stores port delete notifications
        self.deleted_ports = set()

        self.network_ports = collections.defaultdict(set)
        # keeps association between ports and ofports to detect ofport change
        self.vifname_to_ofport_map = {}
        self.setup_rpc()
        self.bridge_mappings = self._parse_bridge_mappings(
            ovs_conf.bridge_mappings)
        self.setup_physical_bridges(self.bridge_mappings)
        self.vlan_manager = vlanmanager.LocalVlanManager()

        self._reset_tunnel_ofports()

        self.polling_interval = agent_conf.polling_interval
        self.minimize_polling = agent_conf.minimize_polling
        self.ovsdb_monitor_respawn_interval = (
            agent_conf.ovsdb_monitor_respawn_interval or
            constants.DEFAULT_OVSDBMON_RESPAWN)
        self.local_ip = ovs_conf.local_ip
        self.tunnel_count = 0
        self.vxlan_udp_port = agent_conf.vxlan_udp_port
        self.dont_fragment = agent_conf.dont_fragment
        self.tunnel_csum = agent_conf.tunnel_csum
        self.tun_br = None
        self.patch_int_ofport = constants.OFPORT_INVALID
        self.patch_tun_ofport = constants.OFPORT_INVALID
        if self.enable_tunneling:
            # The patch_int_ofport and patch_tun_ofport are updated
            # here inside the call to setup_tunnel_br()
            self.setup_tunnel_br(ovs_conf.tunnel_bridge)

        self.init_extension_manager(self.connection)

        self.dvr_agent = ovs_dvr_neutron_agent.OVSDVRNeutronAgent(
            self.context,
            self.dvr_plugin_rpc,
            self.int_br,
            self.tun_br,
            self.bridge_mappings,
            self.phys_brs,
            self.int_ofports,
            self.phys_ofports,
            self.patch_int_ofport,
            self.patch_tun_ofport,
            host,
            self.enable_tunneling,
            self.enable_distributed_routing)

        if self.enable_tunneling:
            self.setup_tunnel_br_flows()

        if self.enable_distributed_routing:
            self.dvr_agent.setup_dvr_flows()

        # Collect additional bridges to monitor
        self.ancillary_brs = self.setup_ancillary_bridges(
            ovs_conf.integration_bridge, ovs_conf.tunnel_bridge)

        # In order to keep existed device's local vlan unchanged,
        # restore local vlan mapping at start
        self._restore_local_vlan_map()

        # Security group agent support
        self.sg_agent = sg_rpc.SecurityGroupAgentRpc(
            self.context, self.sg_plugin_rpc, defer_refresh_firewall=True,
            integration_bridge=self.int_br)

        # we default to False to provide backward compat with out of tree
        # firewall drivers that expect the logic that existed on the Neutron
        # server which only enabled hybrid plugging based on the use of the
        # hybrid driver.
        hybrid_plug = getattr(self.sg_agent.firewall,
                              'OVS_HYBRID_PLUG_REQUIRED', False)
        self.prevent_arp_spoofing = (
            agent_conf.prevent_arp_spoofing and
            not self.sg_agent.firewall.provides_arp_spoofing_protection)

        #TODO(mangelajo): optimize resource_versions to only report
        #                 versions about resources which are common,
        #                 or which are used by specific extensions.
        self.agent_state = {
            'binary': 'neutron-openvswitch-agent',
            'host': host,
            'topic': n_const.L2_AGENT_TOPIC,
            'configurations': {'bridge_mappings': self.bridge_mappings,
                               'tunnel_types': self.tunnel_types,
                               'tunneling_ip': self.local_ip,
                               'l2_population': self.l2_pop,
                               'arp_responder_enabled':
                               self.arp_responder_enabled,
                               'enable_distributed_routing':
                               self.enable_distributed_routing,
                               'log_agent_heartbeats':
                               agent_conf.log_agent_heartbeats,
                               'extensions': self.ext_manager.names(),
                               'datapath_type': ovs_conf.datapath_type,
                               'ovs_capabilities': self.ovs.capabilities,
                               'vhostuser_socket_dir':
                               ovs_conf.vhostuser_socket_dir,
                               portbindings.OVS_HYBRID_PLUG: hybrid_plug},
            'resource_versions': resources.LOCAL_RESOURCE_VERSIONS,
            'agent_type': agent_conf.agent_type,
            'start_flag': True}

        report_interval = agent_conf.report_interval
        if report_interval:
            heartbeat = loopingcall.FixedIntervalLoopingCall(
                self._report_state)
            heartbeat.start(interval=report_interval)
        # Initialize iteration counter
        self.iter_num = 0
        self.run_daemon_loop = True

        self.catch_sigterm = False
        self.catch_sighup = False

        # The initialization is complete; we can start receiving messages
        self.connection.consume_in_threads()

        self.quitting_rpc_timeout = agent_conf.quitting_rpc_timeout
```

*这个初始化函数真尼玛长啊。*

1. 创建 `ovs_lib.BaseOVS` 的实例 ovs，用来执行 ovs 的相关命令（`ovs_lib.BaseOVS` 我在 *agent/ovs* 内分析过）。
2. 'br_int', 'br_phys', 'br_tun' 三个桥的类增加新的参数，目前这些桥所拥有的参数如下：
 1. `ryu_app=self` 这个是在 `OVSNeutronAgentRyuApp.start` 中，`self` 指的是 `OVSNeutronAgentRyuApp` 的实例
 2. `datapath_type=ovs_conf.datapath_type`：使用什么类型的 ovs datapath，默认为 system
3. `use_veth_interconnection` 是否使用 veth 类型的网卡替代 ovs patch 类型的网卡来连接网桥，默认为 False。
4. `veth_mtu` veth 设备的 mtu 值，默认为 9000
5. `available_local_vlans` 可用的 vlan 号
6. `tunnel_types` 隧道网络类型，我们这里使用 vxlan
7. `l2_population` 是否使用 `ML2 l2population mechanism`，默认为 false
8. `enable_distributed_routing` 是否使用 DVR 模式，默认为 False
9. `arp_responder`：是否支持 arp response（这个需要开启 `arp_responder` 和 `l2_population` 的配置）。
10. `host` 主机名
11. `agent_id`
12. `self.enable_tunneling = bool(self.tunnel_types)`
13. 调用 `_check_agent_configurations` 检查配置参数是否合法
14. `int_br_device_count` br_int bridge 上的网络设备的数量
15. 初始化 `OVSIntegrationBridge` 为 `int_br`
16. 调用 `setup_integration_br` 创建 br-int bridge，并且初始化流表配置
17. 调用 `setup_rpc` 初始化 RPC 的相关设置
18. 调用 `_parse_bridge_mappings` 解析 `bridge_mappings`（<physical_network>:<physical_bridge>）（配置文件中为：`bridge_mappings = public:br-ex`）
19. 调用 `setup_physical_bridges` 确保 `physical_bridge`（`br-ex`）存在，并且将 br-ex 与 br-int 相连接
20. 构造 `LocalVlanManager` 的实例 `vlan_manager`
















### `def _check_agent_configurations(self)`

```
    def _check_agent_configurations(self):
        if (self.enable_distributed_routing and self.enable_tunneling
            and not self.l2_pop):

            raise ValueError(_("DVR deployments for VXLAN/GRE/Geneve "
                               "underlays require L2-pop to be enabled, "
                               "in both the Agent and Server side."))
```

### `def setup_integration_br(self)`

1. 调用 `int_br.create` 方法（在 `OVSBridge` 中实现）创建 br-int bridge
2. 调用 `int_br.set_secure_mode` 方法（在 `OVSBridge` 中实现）设置 bridge fail mode 为 security
3. 调用 `int_br.setup_controllers` 方法（在 `OVSAgentBridge` 中实现）为 bridge 设置 controller （`tcp:127.0.0.1:6633`）
4. `drop_flows_on_start` 在 ovs agent 启动时是否重设 flow table，默认为 False。
5. 若是 `drop_flows_on_start` 为 True，则会删除 `int_peer_patch_port`（`patch-tun`）并删除 br-int 上的所有流表
6. 调用 `int_br.setup_default_table` 为 br-int 设置一些默认的流表项

### `def setup_rpc(self)`

1. 实例化 `OVSPluginApi` 作为 RPC Client 和 Neutron Server 进行通信
2. 实例化 `SecurityGroupServerRpcApi` 作为 RPC Client 和 Neutron Server 进行通信
3. 实例化 `DVRServerRpcApi` 作为 RPC Client 和 Neutron Server 进行通信
4. 实例化 `PluginReportStateAPI` 做为 RPC Client 来想 Neutron Server 汇报自身状态
5. 调用 `agent_rpc.create_consumers` 创建 RPC Client，自身作为 endpoint

### `def _parse_bridge_mappings(self, bridge_mappings)`

解析 `bridge_mappings` 配置（`bridge_mappings = public:br-ex`）返回值为：`{'public':'br-ex'}`

### `def setup_physical_bridges(self, bridge_mappings)`

1. 判断 `bridge_mappings` 里面的 bridge 是否存在，若是不存在则会直接退出（**所以，若是要手动创建 physical network 时，需要首先建立对应的 bridge**）。
2. 初始化 `OVSPhysicalBridge` 实例为 br
3. 调用 `br.create` 方法创建 br-ex bridge（**已经手动创建，该命令可以用来设置 datapath**）
4. 调用 `br.set_secure_mode` 设定 br-ex 的 fail mode 为 security
5. 调用 `br.setup_controllers` 设定 br-ex 的 controller 为 `tcp:127.0.0.1:6633`
6. 若 `drop_flows_on_start` 为 True，则情况 br-ex 上的所有流表
7. 构造用来连接 br-int 和 br-ex 的 patch port 的名称，分别为 `'int-br-ex'` 和 `'phy-br-ex'`
8. `use_veth_interconnection` 用来设定采用 veth 类型还是 ovs patch 类型来连接 br-int 和 br-ex，这里我们采用 ovs patch
9. 检查 patch port 是否存在，不存在则创建 patch port，并获取这一对 port 的 ofport 属性
10. 在这一对 patch port 上增加一条 openflow entity
 1. br-int : `cookie=0x921ddac04233086b, duration=9949.994s, table=0, n_packets=9, n_bytes=1427, idle_age=65534, priority=2,in_port=1 actions=drop`
 2. br-ex：`cookie=0x87b735a9a2c26a55, duration=10052.354s, table=0, n_packets=14039, n_bytes=1654098, idle_age=57, priority=2,in_port=1 actions=drop`
 3. **作用：block all untranslated traffic between bridges**




















