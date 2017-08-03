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
20. 构造 `LocalVlanManager` 的实例 `vlan_manager` 用来管理网络与 vlan 的映射关系
21. 调用 `_reset_tunnel_ofports` 设置 `tun_br_ofports` 为空
22. `polling_interval` agent 会轮询本地设备的变动，这个设置就是轮询的间隔时间，默认为 2s。
23. `minimize_polling` 通过检测 ovsdb 中 interface 的变动来减少轮询的耗费，默认为 True。
24. `ovsdb_monitor_respawn_interval` 当于 ovsdb 失去连接后，重启 ovsdb monitor 的间隔时间，默认为 30s。
25. `local_ip` tunnel network 的 endpoint ip 地址（ip 版本 需要与 `overlay_ip_version` 中设定的一致）。
26. `vxlan_udp_port` 默认为 4789
27. `dont_fragment` 是否允许 GRE/VXLAN 数据包分片，默认为 True
28. `tunnel_csum` 是都设置 GRE/VXLAN 的 checksum 默认为 false
29. `tunnel_bridge` 用作隧道的 bridge，默认为 br-tun
29. 若是允许了隧道网络，则调用 `setup_tunnel_br` 初始化 br-tun bridge 的设定
30. 调用 `init_extension_manager` 完成 l2 extension 的初始化工作
31. 实例化 `OVSDVRNeutronAgent` 为 dvr_agent
32. 若 l2 支持 tunnel network，则调用 `setup_tunnel_br_flows`初始化 br-tun 的流表
33. 若 `enable_distributed_routing` 为真，则调用 `dvr_agent.setup_dvr_flows` 初始化 dvr 相关的流表
34. 调用 `setup_ancillary_bridges` 查找出与 neutron 无关的 bridge
35. 调用 `_restore_local_vlan_map` 发现当前已经使用的 vlan 号
36. 实例化 `SecurityGroupAgentRpc` 为 `sg_agent`
37. `prevent_arp_spoofing` 是否防止 ARP 欺诈，默认为 True（这会禁止与源自其所属端口的IP地址不匹配的ARP响应）。
38. 同 dhcp agent 一样开始循环运行 `_report_state` 来报告 ovs agent 的状态
39. 启动 dhcp 的监听


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

### `def _reset_tunnel_ofports(self)`

```
    def _reset_tunnel_ofports(self):
        self.tun_br_ofports = {p_const.TYPE_GENEVE: {},
                               p_const.TYPE_GRE: {},
                               p_const.TYPE_VXLAN: {}}
```

### `def setup_tunnel_br(self, tun_br_name=None)`

作用：初始化用于 tunnel 的 bridge，创建与 br-int 相连接的 patch port

1. 创建 br-tun 网桥
2. 为 br-tun 设定控制器
3. 在 br-tun 和 br-int 增加一对 patch port（分别为：patch-int、patch-tun）。
4. 若是 `drop_flows_on_start` 为真，则删除 br-tun 上的所有流表

### `def init_extension_manager(self, connection)`

1. 实例化 `L2AgentExtensionsManager` 为 `ext_manager`
2. 实例化 `OVSAgentExtensionAPI` 为 `agent_api`
3. 调用 `ext_manager.initialize` 完成 l2 extension 的初始化操作

### `def setup_tunnel_br_flows(self)`

```
    def setup_tunnel_br_flows(self):
        '''Setup the tunnel bridge.

        Add all flows to the tunnel bridge.
        '''
        self.tun_br.setup_default_table(self.patch_int_ofport,
                                        self.arp_responder_enabled)
```

初始化 br-tun 的流表

### `def setup_ancillary_bridges(self, integ_br, tun_br)`

查找出与 neutron 无关的 bridge

### `def _restore_local_vlan_map(self)`

发现当前已经使用的 vlan 号

### `def _report_state(self)`

报告 ovs agent 状态的方法

若是 ovs agent 的状态为 `c_const.AGENT_REVIVED`，则： `self.fullsync = True`

### `def local_vlan_map(self)`

```
    @debtcollector.removals.removed_property(
        version='Newton', removal_version='Ocata')
    def local_vlan_map(self):
        """Provide backward compatibility with local_vlan_map attribute"""
        return self.vlan_manager.mapping
```

### `def daemon_loop(self)`

```
    def daemon_loop(self):
        # Start everything.
        LOG.info(_LI("Agent initialized successfully, now running... "))
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._handle_sighup)
        with polling.get_polling_manager(
            self.minimize_polling,
            self.ovsdb_monitor_respawn_interval) as pm:

            self.rpc_loop(polling_manager=pm)
```

1. 使用 `_handle_sigterm` 处理 `SIGTERM` 信号
2. 使用 `_handle_sighup` 处理 `SIGHUB` 信号
3. 创建一个 `ovsdb-client monitor Interface name,ofport,external_ids --format json` 的包装监测实例 pm
4. 调用 `rpc_loop`

### `def _handle_sigterm(self, signum, frame)`

```
    def _handle_sigterm(self, signum, frame):
        self.catch_sigterm = True
        if self.quitting_rpc_timeout:
            self.set_rpc_timeout(self.quitting_rpc_timeout)
```

### `def _handle_sighup(self, signum, frame)`

```
    def _handle_sighup(self, signum, frame):
        self.catch_sighup = True
```

### `def rpc_loop(self, polling_manager=None)`

1. 调用 `_check_and_handle_signal` 判断接收到的信号（若是接收到 sigterm 信号，则会退出 rpc_loop；若是接收到 sighup 信号则会重新加载配置）
2. 当 ovs agent 发生重启操作时，`self.fullsync` 会置为 True。
3. `iter_num` 代表当前执行 rpc 同步操作的次数
4. 调用 `check_ovs_status` 检查 ovs 的状态
5. 若 ovs 为 `OVS_RESTARTED` 的状态，则：
 1. 调用 `setup_integration_br` 初始化 br-int 
 2. 调用 `setup_physical_bridges` 初始化 br-ex 
 3. 若是可以使用 tunnel network，则
  1. 调用 `_reset_tunnel_ofports` 重置 ofport 的记录
  2. 调用 `setup_tunnel_br` 初始化 br-tun
  3. 调用 `setup_tunnel_br_flows` 初始化 br-tun 的流表
 4. 若是使用 DVR，则：
  1. 调用 `dvr_agent.reset_ovs_parameters` 重置 dvr_agent 的参数
  2. 调用 `dvr_agent.reset_dvr_parameters` 将 dvr 的记录置空
  3. 调用 `setup_dvr_flows` 初始化相关与 dvr 相关的流表
 5. 启动对 ovsdb Interface 的监测
6. 若 ovs 为 `OVS_DEAD` 的状态，此时 ovs agent 不会做其他的处理，仍然后继续进行循环处理
7. 如果允许 tunnel network，且 `tunnel_sync` 为 True（ovs 的状态为 `OVS_RESTARTED` 时。）则会调用 `tunnel_sync` 进行同步操作
8. 判断该 l2 agent 是否需要更新和同步操作：
















### `def _check_and_handle_signal(self)`

```
    def _check_and_handle_signal(self):
        if self.catch_sigterm:
            LOG.info(_LI("Agent caught SIGTERM, quitting daemon loop."))
            self.run_daemon_loop = False
            self.catch_sigterm = False
        if self.catch_sighup:
            LOG.info(_LI("Agent caught SIGHUP, resetting."))
            self.conf.reload_config_files()
            config.setup_logging()
            LOG.debug('Full set of CONF:')
            self.conf.log_opt_values(LOG, logging.DEBUG)
            self.catch_sighup = False
        return self.run_daemon_loop
```

1. 捕捉到 `sigterm` 信号，则将 `run_daemon_loop` 置为 True，这意味着会退出 rpc_loop
2. 捕捉到 `sighup` 信号，则会重新加载配置

### `def check_ovs_status(self)`

调用 `int_br.check_canary_table` 判断 br-int 中 23 号流表是否存在记录，若是存在则认为 ovs 是 `OVS_NORMAL` 的状态，否则是 `OVS_RESTARTED` 的状态

### `def get_port_stats(self, port_info, ancillary_port_info)`

整理 bridge 上 port 变得的信息

### `def tunnel_sync(self)`

1. 通过 rpc 调用 server 端（`TunnelRpcCallbackMixin`）的 `tunnel_sync` 方法（`TunnelRpcCallbackMixin` 中实现）来将该 agent 的 endpoint 信息发送给 neutron-server。neutron-server 会再通过 RPC 消息通知别的 l2 agent。其他的 l2 agent 收到新的 endpoint 消息后会创建对应的 vtep，并增加相应的流表。
2. 调用 server 端的 `tunnel_sync` 方法还会获取当前所有 endpoint 的信息
3. 若不支持 `l2_pop`，则调用 `_setup_tunnel_port` 创建与所有 endpint 对应的 vtep，并创建相应的流表

### `def tunnel_delete(self, context, **kwargs)`

接收 neutron server 传递过来的 tunnel endpoint 删除的消息

1. 检查 endpoint 参数的正确性
2. 获取 `tun_br_ofports` 中记录的被与被删除的 endpoint 对应的 ofport
3. 调用 `cleanup_tunnel_port` 删改该 port 并清除与之相关的 flow

### `def tunnel_update(self, context, **kwargs)`

接收 neutron server 传递过来的 tunnel endpoint 更新的消息

1. 检查 rpc 数据是否正确
2. 若 tunnel ip 等于自身的 local ip 则忽略这次通知（无需为自己建立 vtep）
3. 调用 `get_tunnel_name` 获取对应该 endpoint 的 vtep 的名称
4. 若是不支持 `l2 population` 的话，则调用 `_setup_tunnel_port` 以创建对应该 endpoint 的 vtep，并创建相应的流表

### `def cleanup_tunnel_port(self, br, tun_ofport, tunnel_type)`

检查该 tunnel port 是否还在使用，若不再使用则删除它。

1. 调用 `get_tunnel_name` 获取该与该 endpoint 对应的 vtep 名称
2. 调用 br-run 的 `delete_port` （在 `OVSBridge` 中实现）从该网桥上删除该 Port
3. 调用 br-tun 的 `cleanup_tunnel_port` 删除该 ofport 上的流表记录

### `def get_tunnel_name(cls, network_type, local_ip, remote_ip)`

1. 调用 `get_tunnel_hash` 根据 ip 地址构造一个 hash 值
2. 构造该机器上 vetp 的名称。**由这里我们知道：neutron中 VTEP 的名称是由两部分构成的：该 tunnel nwtork 的类型，及其对端的地址**

### `def get_tunnel_hash(cls, ip_address, hashlen)`

根据 ip 地址构造一个 hash 值

### `def _setup_tunnel_port(self, br, port_name, remote_ip, tunnel_type)`

1. 调用 br-tun 的 `add_tunnel_port`（`OVSBridge`）中实现创建一个 tunnel port。
2. 在属性 `tun_br_ofports` 增加一个 endpoint 与 vtep 的对应记录
3. 调用 br-tun 的 `setup_tunnel_port` 增加一个 flow 记录（对于从此端口进入的数据转发到表 4 中处理）。
4. 若该 agent 不支持 `l2_pop`，则调用 `install_flood_to_tun` 为该 port 增加处理广播信息的功能


```
        Port "vxlan-ac106433"
            Interface "vxlan-ac106433"
                type: vxlan
                options: {df_default="true", in_key=flow, local_ip="172.16.100.192", out_key=flow, remote_ip="172.16.100.51"}
```

```
cookie=0x8d92abaa691e5b6d, duration=177624.860s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,in_port=3 actions=resubmit(,4)
```
```
 cookie=0x8ca031df7a84a666, duration=1178.439s, table=22, n_packets=0, n_bytes=0, idle_age=65534, priority=1,dl_vlan=1 actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:2,output:3
 cookie=0x8ca031df7a84a666, duration=1177.326s, table=22, n_packets=0, n_bytes=0, idle_age=65534, priority=1,dl_vlan=2 actions=strip_vlan,load:0x34->NXM_NX_TUN_ID[],output:2,output:3
```

### `def _agent_has_updates(self, polling_manager)`

```
    def _agent_has_updates(self, polling_manager):
        return (polling_manager.is_polling_required or
                self.updated_ports or
                self.deleted_ports or
                self.sg_agent.firewall_refresh_needed())
```

判断 agent 是否需要有更新的操作

### `def port_update(self, context, **kwargs)`

接收到来自 neutron-server 的 RPC 调用。
记录需要更新的 port 的 id

### `def port_delete(self, context, **kwargs)`

接收到来自 neutron-server 的 RPC 调用。
记录需要删除的 port 的 id

### `def fdb_add(self, context, fdb_entries)`

1. 调用 `get_agent_ports` （在 `L2populationRpcCallBackTunnelMixin` 中实现）根据 fdb entity 获取与之对应的 lvm
2. 忽略关于本机上的 port 更新，对于非本机的 port 更新：
3. 调用 `fdb_add_tun`（在 `L2populationRpcCallBackTunnelMixin` 中实现）

### `def _tunnel_port_lookup(self, network_type, remote_ip)`

```
    def _tunnel_port_lookup(self, network_type, remote_ip):
        return self.tun_br_ofports[network_type].get(remote_ip)
```

获取 vtep

### `def setup_tunnel_port(self, br, remote_ip, network_type)`

调用 `_setup_tunnel_port` 创建该 vtep 并且创建与之相关的流表

### `def add_fdb_flow(self, br, port_info, remote_ip, lvm, ofport)`

1. 若 `port_info` 等于 `FLOODING_ENTRY`，则意味该 agent 刚刚启动，其 vtep（ofport）也刚刚创建，我们为其设定初始的 flow entity。
2. 对于其他的 `port_info`：
 1. 调用 `setup_entry_for_arp_reply` 创建 arp response 的流表
 2. 调用 br-tun 的 `install_unicast_to_tun` 方法，指定访问该 mac 的单播 flow entity


### `def setup_entry_for_arp_reply(self, br, action, local_vid, mac_address, ip_address)`

1. 若该 agent 不支持 `arp_responder_enabled`，则直接返回
2. 若 action 为 `add`，则调用 br-tun 的 `install_arp_responder` 方法创建 arp 回复的 flow entity
3. 若 action 为 `remove`，则调用 br-tun 的 `delete_arp_responder` 方法删除 arp 回复的 flow entity

### `def fdb_remove(self, context, fdb_entries)`

删除 fdb 表项














