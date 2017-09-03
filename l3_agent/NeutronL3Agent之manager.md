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
10. 初始化 `RouterProcessingQueue` 实例，用来记录 router 的更新操作
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

### `def after_start(self)`

```
    def after_start(self):
        # Note: the FWaaS' vArmourL3NATAgent is a subclass of L3NATAgent. It
        # calls this method here. So Removing this after_start() would break
        # vArmourL3NATAgent. We need to find out whether vArmourL3NATAgent
        # can have L3NATAgentWithStateReport as its base class instead of
        # L3NATAgent.
        eventlet.spawn_n(self._process_routers_loop)
        LOG.info(_LI("L3 agent started"))
```

该方法在子类 `L3NATAgentWithStateReport` 中被重写


### `def _process_routers_loop(self)`

```
    def _process_routers_loop(self):
        LOG.debug("Starting _process_routers_loop")
        pool = eventlet.GreenPool(size=8)
        while True:
            pool.spawn_n(self._process_router_update)
```

启动一个绿色线程池来运行 `_process_router_update` 方法

### `def _process_router_update(self)`

* 调用 `RouterProcessingQueue.each_update_to_next_router` 方法，循环获得每个 router 的更新信息
 1. 若更新的动作为 `PD_UPDATE`，则调用 `PrefixDelegation.process_prefix_update` 方法
 2. 获取待更新的 router 数据
 3. 若更新的动作为 `DELETE_ROUTER`，但是未找到 router 数据，则：
  1. 调用 `plugin_rpc.get_routers` 获取 router 的数据
  2. 若发生异常，则调用 `_resync_router` 方法，增加更新 router 数据的任务
 4. 若不存在 router 数据，则：
  1. 调用 `_safe_router_removed` 删除与 router 相关的数据和 namespace
  2. 若删除失败，则调用 `_resync_router` 方法，增加更新 router 数据的任务
  3. 若删除成功，则调用 `ExclusiveRouterProcessor.fetched_and_processed` 方法记录 router 更新的时间
 5. 对于其他情况：
  1. 调用 `_process_router_if_compatible` 处理该 router 的数据（增加或者更新记录）
  2. 调用 `ExclusiveRouterProcessor.fetched_and_processed` 记录该 router 的当前操作时间


### `def router_deleted(self, context, router_id)`

RPC Server endpoint 方法一枚。

### `def _resync_router(self, router_update, priority=queue.PRIORITY_SYNC_ROUTERS_TASK)`

```
    def _resync_router(self, router_update,
                       priority=queue.PRIORITY_SYNC_ROUTERS_TASK):
        router_update.timestamp = timeutils.utcnow()
        router_update.priority = priority
        router_update.router = None  # Force the agent to resync the router
        self._queue.add(router_update)
```

增加一个更新 router 数据的任务

### `def _safe_router_removed(self, router_id)`

1. 调用 `_router_removed` 实现 router 的删除
2. 调用 `l3_ext_manager.delete_router` 处理 extension 
3. 若删除成功，则返回 True
4. 若发生异常，则返回 False

### `def _router_removed(self, router_id)`

1. 若 `router_info` 中不存在有该 router 的记录，则调用 `namespaces_manager.ensure_router_cleanup` 清除与该 router 有关的 namespace
2. 若 `router_info` 中存在有该 router 的记录，则调用 router info delete 删除该 router，并删除 `router_info` 中的记录 

### `def _process_router_if_compatible(self, router)`

1. 若设置了 `external_network_bridge`，则需要检查此网络设备是否存在
2. 获取 router 上 gateway port 所在的 external network
3. 若该 router 不存在 external network 且未设置 `handle_internal_only_routers`，则引发异常
4. 若是通过 `_fetch_external_net_id` 获取的 external network id 与 router gateway port 所在的 external networ id 不一致，则引发异常
5. 若该 router 的 id 未在当前 l3 agent 的记录中，则调用 `_process_added_router` 用来增加该 router 的记录
6. 若该 router 的 id 属性已经在当前 l3 agent 的记录中，则调用 `_process_updated_router` 更新该 router 记录的数据

* **配置选项说明**：
 1. `external_network_bridge`（这个配置选项将在 O 版本被删除）若配置了该选项，那么所有附加在该 bridge 上的 port 都不再由 l2 agent 来管理
 2. `handle_internal_only_routers`：当一个 router 没有 gateway 是，是否可以使用，也就是 router 是否可以用来只处理内部网络。
 3. `gateway_external_network_id`：当 `external_network_bridge` 设定后，每个 l3 agent 只能帮到一个 external network，`gateway_external_network_id` 就是用来声明该 external network id 的（若是想要一个 l3 agent 支持多个 external network，这两个选项必须同时设定为空）。

### `def _fetch_external_net_id(self, force=False)`

该方法只有在设置了 `gateway_external_network_id` 或者 `external_network_bridge` 的情况下生效。

1. 若设置了 `gateway_external_network_id`，则返回此值
2. 若未设置 `external_network_bridge` 则返回空
3. 若未设置 `force`，且存在 `self.target_ex_net_id`，则返回 `target_ex_net_id`
4. 调用 `plugin_rpc.get_external_network_id` 获取 external network id，返回此值

### `def _process_added_router(self, router)`

1. 调用 `_router_added` 创建该 router info 的记录
2. 调用 router info 的 `process` 方法
3. 通过 callback system 发送 ROUTER AFTER_CREATE 的通知
4. 若存在 l3 extension，则调用 extension 的 `add_router` 方法

### `def _router_added(self, router_id, router)`

1. 调用 `_create_router` 创建 router 的描述
2. 通过 callback system 发送 ROUTER BEFORE_CREATE 的通知
3. 在当前的 l3 agent 中记录 router 数据
4. 调用 router 的 `initialize` 方法

### `def _create_router(self, router_id, router)`

```
    def _create_router(self, router_id, router):
        args = []
        kwargs = {
            'router_id': router_id,
            'router': router,
            'use_ipv6': self.use_ipv6,
            'agent_conf': self.conf,
            'interface_driver': self.driver,
        }

        if router.get('distributed'):
            kwargs['agent'] = self
            kwargs['host'] = self.host

        if router.get('distributed') and router.get('ha'):
            if self.conf.agent_mode == lib_const.L3_AGENT_MODE_DVR_SNAT:
                kwargs['state_change_callback'] = self.enqueue_state_change
                return dvr_edge_ha_router.DvrEdgeHaRouter(*args, **kwargs)

        if router.get('distributed'):
            if self.conf.agent_mode == lib_const.L3_AGENT_MODE_DVR_SNAT:
                return dvr_router.DvrEdgeRouter(*args, **kwargs)
            else:
                return dvr_local_router.DvrLocalRouter(*args, **kwargs)

        if router.get('ha'):
            kwargs['state_change_callback'] = self.enqueue_state_change
            return ha_router.HaRouter(*args, **kwargs)

        return legacy_router.LegacyRouter(*args, **kwargs)
```

根据 router 的类型，创建一个 `RouterInfo` 的子类实例来描述 router

### `def _process_updated_router(self, router)`

1. 更新当前 l3 agent 中关于该 router 记录的数据
2. 通过 callback system 发送 ROUTER BEFORE_UPDATE 的通知
3. 若存在 l3 extension，则调用 extension 的 `update_router` 方法

### `def periodic_sync_routers_task(self, context)`

这个是间隔一段时间执行的任务，用来完成 l3 agent 与 Router Servic 的信息同步。

1. 若 `fullsync` 为 false，则直接返回
2. 若 `fullsync` 为 True，则调用 `fetch_and_sync_all_routers` 与 Neutron Server 进行 router 数据的同步

### `def fetch_and_sync_all_routers(self, context, ns_manager)`

1. 调用 `plugin_rpc.get_router_ids` 获取该 l3 agent 上所有 router 的 id
2. 调用 `plugin_rpc.get_routers` 获取一定数量的 router 数据
3. 对于所获得的 router 的数据：
 1. 若该 router 是 distributed，
  1. 调用 `NamespaceManager` 记录该 router 的数据
  2. 若当前的 l3 agent 是 dvr_snat 模式，则调用 `NamespaceManager.ensure_snat_cleanup` 清理与该 router 有关的 snat namespace
 2. 若该 router 支持 ha，则：
  1. 调用 `check_ha_state_for_router` 检查该 ha router 的状态是否发生了变化
 3. 根据 router 的数据生成一个 `RouterUpdate` 的实例，并将其放入待处理的队列中
4. 若所有的 router 数据都同步成功，则根据同步前的 router 数据和同步后的 router 数据，找出那些需要被删除的 router
5. 为这些需要被删除的 router 创建 `RouterUpdate` 对象，放入待处理队列中

### `def router_removed_from_agent(self, context, payload)`

创建 `RouterUpdate` 的事件（`DELETE_ROUTER`），并将其放入待处理队列中

### `def router_added_to_agent(self, context, payload)`

调用 `routers_updated` 实现

### `def routers_updated(self, context, routers)`

针对所有待操作的 router 数据，创建 `RouterUpdate` 事件，并将其放入事件队列中。

### `def create_pd_router_update(self)`

关于 ipv6 处理的，待深入了解