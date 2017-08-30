# Neutron l3 agent 之 manager

此 manager 既是 RPC Server endpint。

RPC Client 为：`L3AgentNotifyAPI`

## `class L3NATAgentWithStateReport(L3NATAgent)`

*neutron/agent/l3/agent.py*

```
    def __init__(self, host, conf=None):
        super(L3NATAgentWithStateReport, self).__init__(host=host, conf=conf)
        self.state_rpc = agent_rpc.PluginReportStateAPI(topics.REPORTS)
        self.agent_state = {
            'binary': 'neutron-l3-agent',
            'host': host,
            'availability_zone': self.conf.AGENT.availability_zone,
            'topic': topics.L3_AGENT,
            'configurations': {
                'agent_mode': self.conf.agent_mode,
                'handle_internal_only_routers':
                self.conf.handle_internal_only_routers,
                'external_network_bridge': self.conf.external_network_bridge,
                'gateway_external_network_id':
                self.conf.gateway_external_network_id,
                'interface_driver': self.conf.interface_driver,
                'log_agent_heartbeats': self.conf.AGENT.log_agent_heartbeats},
            'start_flag': True,
            'agent_type': lib_const.AGENT_TYPE_L3}
        report_interval = self.conf.AGENT.report_interval
        if report_interval:
            self.heartbeat = loopingcall.FixedIntervalLoopingCall(
                self._report_state)
            self.heartbeat.start(interval=report_interval)
```

启动一个 RPC Client `PluginReportStateAPI` 用于向 neutron-server 报告 l3 agent 的状态。

### `def _report_state(self)`

向 neutron-server 汇报 l3 agent 的详细信息。
若判断 l3 agent 的状态为 `AGENT_REVIVED` 则会将 `self.fullsync` 置为 True

### `def after_start(self)`

1. 启动一个线程运行 `_process_routers_loop` 方法（`L3NATAgent` 中实现）
2. 调用 `_report_state` 汇报一下当前 l3 agent 的状态
3. 调用 `pd.after_start` 设定 pd 的信号处理程序。

### `def agent_updated(self, context, payload)`

```
    def agent_updated(self, context, payload):
         """Handle the agent_updated notification event."""
        self.fullsync = True
        LOG.info(_LI("agent_updated by server side %s!"), payload)
```

这是一个 RPC Server endpoint 方法。

当有 agent update 发生时，将 fullsyn 置为 True

在 neutron-server 端，收到将 l3 agent 的 `admin_state_up` 属性改变的操作时，会触发该 RPC 调用。

## `class L3NATAgent(ha.AgentMixin, dvr.AgentMixin, manager.Manager)`

```
    target = oslo_messaging.Target(version='1.3')

    def __init__(self, host, conf=None):
        if conf:
            self.conf = conf
        else:
            self.conf = cfg.CONF
        self.router_info = {}

        self._check_config_params()

        self.process_monitor = external_process.ProcessMonitor(
            config=self.conf,
            resource_type='router')

        self.driver = common_utils.load_interface_driver(self.conf)

        self._context = n_context.get_admin_context_without_session()
        self.plugin_rpc = L3PluginApi(topics.L3PLUGIN, host)
        self.fullsync = True
        self.sync_routers_chunk_size = SYNC_ROUTERS_MAX_CHUNK_SIZE

        # Get the list of service plugins from Neutron Server
        # This is the first place where we contact neutron-server on startup
        # so retry in case its not ready to respond.
        while True:
            try:
                self.neutron_service_plugins = (
                    self.plugin_rpc.get_service_plugin_list(self.context))
            except oslo_messaging.RemoteError as e:
                with excutils.save_and_reraise_exception() as ctx:
                    ctx.reraise = False
                    LOG.warning(_LW('l3-agent cannot check service plugins '
                                    'enabled at the neutron server when '
                                    'startup due to RPC error. It happens '
                                    'when the server does not support this '
                                    'RPC API. If the error is '
                                    'UnsupportedVersion you can ignore this '
                                    'warning. Detail message: %s'), e)
                self.neutron_service_plugins = None
            except oslo_messaging.MessagingTimeout as e:
                with excutils.save_and_reraise_exception() as ctx:
                    ctx.reraise = False
                    LOG.warning(_LW('l3-agent cannot contact neutron server '
                                    'to retrieve service plugins enabled. '
                                    'Check connectivity to neutron server. '
                                    'Retrying... '
                                    'Detailed message: %(msg)s.'), {'msg': e})
                    continue
            break

        self.init_extension_manager(self.plugin_rpc)

        self.metadata_driver = None
        if self.conf.enable_metadata_proxy:
            self.metadata_driver = metadata_driver.MetadataDriver(self)

        self.namespaces_manager = namespace_manager.NamespaceManager(
            self.conf,
            self.driver,
            self.metadata_driver)

        self._queue = queue.RouterProcessingQueue()
        super(L3NATAgent, self).__init__(host=self.conf.host)

        self.target_ex_net_id = None
        self.use_ipv6 = ipv6_utils.is_enabled()

        self.pd = pd.PrefixDelegation(self.context, self.process_monitor,
                                      self.driver,
                                      self.plugin_rpc.process_prefix_update,
                                      self.create_pd_router_update,
                                      self.conf)
```

1. 调用 `_check_config_params` 检查配置参数是否有问题（主要是检查 `interface_driver` 有没有配置）
2. 创建一个 `ProcessMonitor` 的实例 `process_monitor` 用来监测外部执行的进程
3. 加载接口驱动，并初始化为 driver。
 * 根据配置，接口驱动为 openvswitch（对应：`neutron.agent.linux.interface:OVSInterfaceDriver`）
4. 构造一个 context 实例
5. 初始化 `L3PluginApi` 实例 plugin_rpc，用作 RPC Client 来与 neutron server 进行通信
6. 调用 `plugin_rpc.get_service_plugin_list` 获取 neutron-server 中启用的 service plugin 的列表
7. 调用 `init_extension_manager` 初始化 extension
8. 若是允许使用 metadata proxy，则会加载 `metadata_driver.MetadataDriver` 实例
9. 初始化 `NamespaceManager` 实例
10. 初始化 `RouterProcessingQueue` 实例
11. 调用父类的初始化方法
12. 判断是否使用 ipv6
13. 构造 `PrefixDelegation` 实例

### `def _check_config_params(self)`

1. 检查 `interface_driver` 是否配置
2. 若是设置了 `ipv6_gateway`，则检查：*Check for valid v6 link-local address.*

### `def init_extension_manager(self, connection)`

*l3 agent 目前还没有任何的 extension 可用，所以这里我们只是简单看一下逻辑*

1. 注册配置选项
2. 实例化 `L3AgentExtensionAPI`
3. 实例化 `L3AgentExtensionsManager`
4. 调用 `L3AgentExtensionsManager.initialize` 方法用来初始化 extensions。

### `def _process_routers_loop(self)`

```
    def _process_routers_loop(self):
        LOG.debug("Starting _process_routers_loop")
        pool = eventlet.GreenPool(size=8)
        while True:
            pool.spawn_n(self._process_router_update)
```

启动一个绿色线程来运行 `_process_router_update` 方法

### `def _process_router_update(self)`



1. 调用 `RouterProcessingQueue.each_update_to_next_router` 方法



### `def router_deleted(self, context, router_id)`

RPC Server endpoint 方法一枚。











## `class AgentMixin(object)`

*neutron/agent/l3/ha.py*

```
    def __init__(self, host):
        self._init_ha_conf_path()
        super(AgentMixin, self).__init__(host)
        self.state_change_notifier = batch_notifier.BatchNotifier(
            self._calculate_batch_duration(), self.notify_server)
        eventlet.spawn(self._start_keepalived_notifications_server)
```

1. 调用 `_init_ha_conf_path`
2. 调用 `_calculate_batch_duration`
3. 初始化一个 `BatchNotifier` 的实例
4. 开辟一个线程，运行 `_start_keepalived_notifications_server` 方法

### `def _init_ha_conf_path(self)`

```
    def _init_ha_conf_path(self):
        ha_full_path = os.path.dirname("/%s/" % self.conf.ha_confs_path)
        common_utils.ensure_dir(ha_full_path)
```

确保 ha 数据目录的存在。（本实例为 `/opt/stack/data/neutron/ha_confs/`）

### `def _calculate_batch_duration(self)`

计算 ha salve 切换至 master 所需要的时间

### `def _start_keepalived_notifications_server(self)`

初始化一个 `L3AgentKeepalivedStateChangeServer` 实例
调用 `L3AgentKeepalivedStateChangeServer.run` 方法











## `class AgentMixin(object)`

*neutron/agent/l3/dvr.py*

```
class AgentMixin(object):
    def __init__(self, host):
        # dvr data
        self._fip_namespaces = weakref.WeakValueDictionary()
        super(AgentMixin, self).__init__(host)
```




















