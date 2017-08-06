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

若是 ovs agent 的状态为 `c_const.AGENT_REVIVED`，则： `self.fullsync = True`（这个属性会在 `rpc_loop` 方法中用到，该标志意味这需要进行同步操作）。

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

* 属性说明
 1. sync ：是否需要执行同步操作
 2. ports ：当前 l2 agent 追踪的 port
 3. updated_ports_copy ：self.updated_ports 的 copy 版（rpc 调用会更新这个数据）
 4. ancillary_ports ：当前 l2 agent 追踪的在 `ancillary_brs` （非 br-ex、br-int、br-tun的辅助br）上使用的 port
 5. tunnel_sync ：是否需要对 tunnel 做更新操作
 6. ovs_restarted ：ovs 是否刚刚启动
 7. consecutive_resyncs ：重复更新的次数（上次更新失败，则下次更新时算是重复更新）
 8. need_clean_stale_flow  
 9. ports_not_ready_yet ：port 已经存在，但是没有 ready
 10. failed_devices ：在 neutron-server 端获取详细信息失败的 Port
 11. failed_ancillary_devices ：在 neutron-server 端获取详细信息失败的辅助 Port
 12. failed_devices_retries_map

1. 调用 `_check_and_handle_signal` 判断接收到的信号（若是接收到 sigterm 信号，则会退出 rpc_loop；若是接收到 sighup 信号则会重新加载配置）
2. 当 ovs agent 发生重启操作时，`self.fullsync` 会置为 True。
3. `iter_num` 代表当前执行 rpc 同步操作的次数
4. 调用 `check_ovs_status` 检查 ovs 的状态
5. 若 ovs 为 `OVS_RESTARTED` 的状态，则会重新走一遍初始化的流程：
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
8. 若该 l2 agent 是否需要更新、同步和重试的操作：
 1. 调用 `process_port_info` 获取当前所有 port 的信息（增加、删除、已追踪、未准备好）
 2. 调用 `process_deleted_ports` 将被删除的 port unbind
 3. 调用 `update_stale_ofport_rules` 清除 br-int 上所有与被删除 port 有关的流表项
 4. 若是有 port 的状态发生了变化：
  1. 调用 `process_network_ports` 处理那些增加、更新、删除的 port，返回处理失败的 port
  2. 若需要清空 flow，则调用 `cleanup_stale_flows` 清空所有的 flow
 5. 若存在 `ancillary_brs`
  1. 调用 `process_ancillary_network_ports` 处理所有的 `ancillary_port`
 6. 调用 `polling_manager.polling_completed` 说明本次数据监测处理完成
 7. 调用 `update_retries_map_and_remove_devs_not_to_retry` 整理失败的 port，组织下次重新进行同步的 port 信息
 8. 调用 `_dispose_local_vlan_hints` 同步当前 vlan 的使用信息
9. 调用 `get_port_stats` 统计当前的 port 信息

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

* 判断 agent 是否需要有更新的操作
 1. ovs 数据库发生变动
 2. 有被更新或者删除的 port
 3. 安全组发生变动

### `def port_update(self, context, **kwargs)`

接收到来自 neutron-server 的 RPC 调用。
记录需要更新的 port 的 id

### `def port_delete(self, context, **kwargs)`

接收到来自 neutron-server 的 RPC 调用。
记录需要删除的 port 的 id

### `def fdb_add(self, context, fdb_entries)`

1. 调用 `get_agent_ports` （在 `L2populationRpcCallBackTunnelMixin` 中实现）根据 fdb entity 获取与之对应的 lvm
2. 忽略关于本机上的 port 更新，对于非本机的 port 更新：
3. 调用 `fdb_add_tun`（在 `L2populationRpcCallBackTunnelMixin` 中实现）创建 tunnel port 以及创建相应的 arp response 流表

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

1. 调用 `get_agent_ports` 获取 lvm 和待删除的 port 数据
2. 调用 `fdb_remove_tun` 进行 port 流表的删除工作（arp responser、unicast、flood flow entity）

### `def del_fdb_flow(self, br, port_info, remote_ip, lvm, ofport)`

1. 若 port_info 中包含的是 vtep flooding entry 的消息，则需要去除与此 vetp 有关的 flow entity
 1. 若还有别的 vtep ，则调用 `install_flood_to_tun` 重新布置 flood flow entity
 2. 若没有别的 vtep了则调用 `delete_flood_to_tun` 删除有关该 vlan 的 flow eneity 
2. 若 port_info 中包含的是普通 port 的信息，则：
 1. 调用 `setup_entry_for_arp_reply` 删除与该 port 有关的 arp responser flow entity
 2. 调用 `delete_unicast_to_tun` 删除在 20 号流表中保存的该 port 的单播 flow entity

### `def _fdb_chg_ip(self, context, fdb_entries)`

当收到 neutron-server l2pop mech driver 发来的 mac 地址变成的 fdb 消息时调用 `fdb_chg_ip_tun` 更新与该 port 信息有关的 flow entity。

### `def network_update(self, context, **kwargs)`

```
    def network_update(self, context, **kwargs):
        network_id = kwargs['network']['id']
        for port_id in self.network_ports[network_id]:
            # notifications could arrive out of order, if the port is deleted
            # we don't want to update it anymore
            if port_id not in self.deleted_ports:
                self.updated_ports.add(port_id)
        LOG.debug("network_update message processed for network "
                  "%(network_id)s, with ports: %(ports)s",
                  {'network_id': network_id,
                   'ports': self.network_ports[network_id]})
```

### `def process_port_info`

```
    def process_port_info(self, start, polling_manager, sync, ovs_restarted,
                       ports, ancillary_ports, updated_ports_copy,
                       consecutive_resyncs, ports_not_ready_yet,
                       failed_devices, failed_ancillary_devices)
```

1. 在 sycn 为真或者 `polling_manager` 没有 `get_events` 方法的情况下：
 1. 若 sync 为真则将 consecutive_resyncs 加 1；
 2. 若 sync 为假则将 consecutive_resyncs 置为 0，同时根据 `failed_devices` 和 `failed_ancillary_devices` 判断是否将 sync 置为真
 3. 调用 `scan_ports` 获取在 int-br 上发生增加、删除、更新的所有 port 的 id
 4. 若存在 `ancillary_brs`，则调用 `scan_ancillary_ports` 获取在 `ancillary_brs` 上发生增加、删除、更新的所有 port 的 id
2. 若无需进行 sync 操作，且 `polling_manager` 支持 `get_events` 方法，则：
 1. 调用 `polling_manager.get_events` 获取 ovs 上所有发送变动的 port
 2. 调用 `process_ports_events` 获取 port 的信息
 3. 调用回调系统发送 ovsdb read 完的通知
3. 返回 (port_info, ancillary_port_info, consecutive_resyncs, ports_not_ready_yet)


### `def scan_ports(self, registered_ports, sync, updated_ports=None)`

1. 调用 `int_br.get_vif_port_set` 获取 br-int 上与 network 有关的接口
2. 调用 `_get_port_info` 判断有哪些 port 需要加入追踪，有哪些 port 需要删除
3. 调用 `check_changed_vlans` 查找 vlan_manager 中与 br-int 中不一样的 port 信息，并将这些 port 加入到 `updated_ports` 列表中
4. 综合上述信息，获取在 int-br 上发生增加、删除、更新的 port 的 id，并返回

### `def _get_port_info(self, registered_ports, cur_ports, readd_registered_ports)`

1. `registered_ports` 当前 l2 agent 追踪的 port
2. `cur_ports` 当前 ovs br-int 上的 port
3. `readd_registered_ports` 是否重新读取 ovs br-int 上的 port

作用：根据已有的数据，判断当前 l2 agent 追踪的 port 有哪些需要加入，有哪些需要删除。

### `def check_changed_vlans(self)`

1. 调用 `int_br.get_port_tag_dict` 获取所有 port 的 name 和 tag
2. 将 `vlan_manager` 保存的 port 信息与从 br-int 获取的 port 信息对比，查找 tag 变化的 port 并返回

### `def scan_ancillary_ports(self, registered_ports, sync)`

获取 `ancillary_brs` 上所有再用的 port，然后根据已有的数据（`registered_ports`），判断当前 l2 agent 追踪的 ancillary_port 有哪些需要加入，有哪些需要删除

### `def process_ports_events`

```
    def process_ports_events(self, events, registered_ports, ancillary_ports,
                             old_ports_not_ready, failed_devices,
                             failed_ancillary_devices, updated_ports=None)
```

1. 根据 event 信息，区分出那些 port 被删除、那些 port 被加入
2. 定义一个内部方法 `_process_port`，用来判断该包属于哪个组（未准备好、port、辅助 port）
3. 若存在 `old_ports_not_ready`（上次同步时未准备好的 port）则检查 int-br 上其是否已经准备好还是被删除，将还未准备好的 port 更新到 `ports_not_ready_yet` 中
4. 调用 `_update_port_info_failed_devices_stats` 方法，根据 `failed_devices` 的信息更新 port_info 的信息
5. 调用 `_update_port_info_failed_devices_stats` 方法，根据 `failed_ancillary_devices` 的信息更新 ancillary_port_info 的信息
6. 调用 `check_changed_vlans` 获取 `updated_ports`，在根据 `updated_ports` 来更新 port_info
7. 最后返回完全处理好的 `port_info, ancillary_port_info, ports_not_ready_yet`

返回信息的数据结构如下：

```
        port_info = {}
        port_info['added'] = set() : 新增的
        port_info['removed'] = set()：被移除的
        port_info['current'] = set()：当前追踪的（包含新增的，并且去除了被移除的）

        ancillary_port_info = {}
        ancillary_port_info['added'] = set()：新增的
        ancillary_port_info['removed'] = set()：被移除的
        ancillary_port_info['current'] = set()：当前追踪的（包含新增的，并且出去了被移除的）

        ports_not_ready_yet = set()：还未 ready 的
```


### `def _update_port_info_failed_devices_stats(self, port_info, failed_devices)`

根据 `failed_devices` 的信息更新 port_info 的信息

### `def process_deleted_ports(self, port_info)`

1. 忽略那些已经被删除的 port
2. 调用 `_clean_network_ports` 在 `network_ports` 的属性中删除 port_id 的记录
3. 调用 `ext_manager.delete_port` 调用各个 extension 的 delete_port 的方法
4. 调用 `port_dead` 将该 port 的 tag 置为 `DEAD_VLAN_TAG`，同时丢弃从该 port 进入的数据包
5. 调用 `port_unbound` 释放该 port 所占用的流表项，若该 port 是该 agent 上的最后一个 port，则需要释放该 network 所占有的 local vlan 的所有流表项
6. 调用 `sg_agent.remove_devices_filter` 处理与所有删除 port 的 filter

### `def _clean_network_ports(self, port_id)`

在 `network_ports` 的属性中删除 port_id 的记录

### `def port_dead(self, port, log_errors=True)`

1. 将该 port 的 tag 置为 `DEAD_VLAN_TAG`
2. 设置 flow entity，将从该看 port 进入的数据包 drop

### `def port_unbound(self, vif_id, net_uuid=None)`

1. 调用 `dvr_agent.unbind_port_from_dvr` 解绑这个 port
2. 在 `vlan_manager` 去除该 port 的记录
3. 若此 lvm 中没有了 port，则调用 `reclaim_local_vlan` 回收该（删除） agent 关于此 local vlan 的一切流表记录

### `def reclaim_local_vlan(self, net_uuid)`

取消 vlan manager 中关于此 network 的记录（也就是此 network 不再当前的 agent 上拥有 port 了）

1. 取消在 vlan manager 中的记录 
2. 若此 network 是 tunnel network，则：
 1. 调用 br-tun 的 `reclaim_local_vlan` 方法删除该 network 的 segmentation_id 与 local vlan 转换关系的流表
 2. 调用 br-tun 的 `delete_flood_to_tun` 取消该网络的洪泛转发
 3. 调用 br-tun 的 `delete_unicast_to_tun` 取消转发到该网络的单播流表
 4. 调用 br-tun 的 `delete_arp_responder` 取消对与该 network 有关的 arp 消息的相应 
 5. 若开启了 l2 pop，则还需要调用 `cleanup_tunnel_port` 清除该 port 及其流表
3. 若此网络类型是 flat 类型的 network，则：
 1. 调用 br-ex 的 `reclaim_local_vlan` 删除关于该网络的 local vlan 的流表
 2. 调用 br-int 的 `reclaim_local_vlan` 删除关于该网络的 local vlan 的流表
4. 若此网络类型是 vlan 类型的 network，则：
 1. 调用 br-ex 的 `reclaim_local_vlan` 删除关于该网络的 local vlan 的流表
 2. 调用 br-int 的 `reclaim_local_vlan` 删除关于该网络的 local vlan 的流表
5. 对于 local 类型的 network 不作任何处理

### `def cleanup_tunnel_port(self, br, tun_ofport, tunnel_type)`

1. 首先检查 tunnel port 是否仍在被被的网络使用，若是正在使用则直接退出
2. 若该 tunnel port 不再被使用了，则调用 br-tun 的 `delete_port` 删除该 port，调用 br-tun 的 `cleanup_tunnel_port` 删除与该 port 有关的流表

### `def update_stale_ofport_rules(self)`

1. 调用 `int_br.get_vif_port_to_ofport_map` 获取 br-int 上所有 vif 的 ID 与 ofport 的映射
2. 调用 `_get_ofport_moves` 获取 ofport 发生变化的端口
3. 统计被删除的 ofport 的端口
4. 调用 `int_br.delete_arp_spoofing_protection` 删除 br-int 上与该 port 有关的所有 arp 的表项
5. 调用 `int_br.delete_flows` 删除 br-int 上有该 port 有关的所有 flow entity
6. 更新 `self.vifname_to_ofport_map` 与 br-int 上实际的 port 保持一致

### `def _get_ofport_moves(current, previous)`

总计 ofport 发生变化的端口

### `def _port_info_has_changes(self, port_info)`

```
    def _port_info_has_changes(self, port_info):
        return (port_info.get('added') or
                port_info.get('removed') or
                port_info.get('updated'))
```

### `def process_network_ports(self, port_info, ovs_restarted)`

1. 调用 `treat_devices_added_or_updated` 进行 Port（ovs 上的 port） 的绑定工作
2. 调用 `_add_port_tag_info` 处于那些绑定不成功的进行再次的设定
3. 调用 `sg_agent.setup_port_filters	` 为新加入的 port 增加 filter
4. 调用 `_bind_devices` 实现那些绑定不成功的进行再次的设定
5. 调用 `treat_devices_removed` 解绑那些被移除的 port

### `def treat_devices_added_or_updated(self, devices, ovs_restarted)`

1. 通过 RPC 调用 Server 端的 `get_devices_details_list_and_failed_devices` 方法获取 device 的详细信息，对于获取失败的 device 则归为 `failed_devices`，获取信息成功的 device 则归为 `device` 。
2. 调用 `treat_vif_port` 进行 port 的绑定
3. 调用 `_update_port_network` 更新该 port 的记录信息
4. 调用 `ext_manager.handle_port` 让 extension 去处理刚刚绑定的 port

### `def treat_vif_port(self, vif_port, port_id, network_id, network_type, physical_network, segmentation_id, admin_state_up, fixed_ips, device_owner, ovs_restarted)`

调用 `port_bound`，将该 port 与 network id 绑定（lvm），并设置相关流表。
若绑定成功则返回 True，否则返回 False


### `def port_bound(self, port, net_uuid, network_type, physical_network, segmentation_id, fixed_ips, device_owner, ovs_restarted)`

1. 若是该 port 所在的 network 还没有在 vlan manager 中，则调用 `provision_local_vlan` 在各个网桥上创建相关的流表
2. 调用 `dvr_agent.bind_port_to_dvr` 将该 port 在 dvr 上进行绑定
3. 设置该 port 的 other_config 属性

### `def provision_local_vlan(self, net_uuid, network_type, physical_network, segmentation_id)`

1. 若该 network 在当前的 agent 没有分配 local vlan，则给其分配一个，并记录到 vlan manager 中
2. 若该网络类行为 tunnel network
 1. 调用 `tun_br.install_flood_to_tun` 在 br-tun 上增加该 network 的洪泛流表
 2. 根据是否启用 dvr 调用 `dvr_agent.process_tunneled_network` 创建该 network 在 br-tun 的转发流表还是学习流表
3. 若该 network 为 flat 类型，则调用 `_local_vlan_for_flat` 为该 network 在 br-int 和 br-ex 上创建相关流表
4. 若该 network 为 vlan 类型，则调用 `_local_vlan_for_vlan` 为该 network 在 br-int 和 br-ex 上创建相关流表
5. 若该 network 为 vlan 类型，则不作任何处理


### `def _local_vlan_for_flat(self, lvid, physical_network)`

为 lvid 代表的 flat 类型 network 在 br-ex 和 br-tun 上创建相关流表，处理从外部进来的流量

### `def _local_vlan_for_vlan(self, lvid, physical_network, segmentation_id)`

为 lvid 代表的 vlan 类型 network 在 br-ex 和 br-tun 上创建相关流表，处理从外部进来的流量

### `def _add_port_tag_info(self, need_binding_ports)`

设定 port 的详细信息。（类似于绑定的操作）

### ``


### `def treat_devices_removed(self, devices)`

1. 调用 `plugin_rpc.update_device_list`
2. 调用 `ext_manager.delete_port` 调用所有 extension 的 delete_port 操作
3. 调用 `port_unbound` 解绑 port

### `def cleanup_stale_flows(self)`

调用所有 br 的 `cleanup_flows` 方法 清空所有的 flow 


### `def update_retries_map_and_remove_devs_not_to_retry`

1. 调用 `_get_devices_not_to_retry`
2. 调用 `_remove_devices_not_to_retry`

### `def _get_devices_not_to_retry(self, failed_devices, failed_ancillary_devices, failed_devices_retries_map)`



### `def _remove_devices_not_to_retry(self, failed_devices, failed_ancillary_devices, devices_not_to_retry, ancillary_devices_not_to_retry)`


### `def get_port_stats(self, port_info, ancillary_port_info)`

```
    def get_port_stats(self, port_info, ancillary_port_info):
        port_stats = {
            'regular': {
                'added': len(port_info.get('added', [])),
                'updated': len(port_info.get('updated', [])),
                'removed': len(port_info.get('removed', []))}}
        if self.ancillary_brs:
            port_stats['ancillary'] = {
                'added': len(ancillary_port_info.get('added', [])),
                'removed': len(ancillary_port_info.get('removed', []))}
        return port_stats
```
