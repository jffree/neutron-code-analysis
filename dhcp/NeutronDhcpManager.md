# Neutron dhcp manager

* dhcp agent 的启动代码：

```
def main():
    register_options(cfg.CONF)
    common_config.init(sys.argv[1:])
    config.setup_logging()
    server = neutron_service.Service.create(
        binary='neutron-dhcp-agent',
        topic=topics.DHCP_AGENT,
        report_interval=cfg.CONF.AGENT.report_interval,
        manager='neutron.agent.dhcp.agent.DhcpAgentWithStateReport')
    service.launch(cfg.CONF, server).wait()
```

* dhcp agent 是以一个 service 的方式启动，会运行 `service.start` 方法。
 1. 其实就是以 dhcp manger 实例为 endpoint，以 `dhcp_agent` 为 topic 启动一个 rpc server，topic。（请见文章：neutron中的Service）
 2. client 端为 `neutron.api.rpc.agentnotifiers.dhcp_rpc_agent_api.DhcpAgentNotifyApi`，这一个在 ml2 中被实例化。
 3. dhcp agent 的 manager 为：`neutron.agent.dhcp.agent.DhcpAgentWithStateReport`

## `class DhcpAgentWithStateReport(DhcpAgent)`

### `def __init__(self, host=None, conf=None)`

```
    def __init__(self, host=None, conf=None):
        super(DhcpAgentWithStateReport, self).__init__(host=host, conf=conf)
        self.state_rpc = agent_rpc.PluginReportStateAPI(topics.REPORTS)
        self.agent_state = {
            'binary': 'neutron-dhcp-agent',
            'host': host,
            'availability_zone': self.conf.AGENT.availability_zone,
            'topic': topics.DHCP_AGENT,
            'configurations': {
                'notifies_port_ready': True,
                'dhcp_driver': self.conf.dhcp_driver,
                'dhcp_lease_duration': self.conf.dhcp_lease_duration,
                'log_agent_heartbeats': self.conf.AGENT.log_agent_heartbeats},
            'start_flag': True,
            'agent_type': constants.AGENT_TYPE_DHCP}
        report_interval = self.conf.AGENT.report_interval
        if report_interval:
            self.heartbeat = loopingcall.FixedIntervalLoopingCall(
                self._report_state)
            self.heartbeat.start(interval=report_interval)
```

1. dhcp agent service 创建的时候，没有声明 host，所以采用配置文件中声明的 host：`cfg.CONF.host`
2. `dhcp_driver_cls` 在配置文件 */etc/neutron/dhcp_agent.ini* 中为：`dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq`
3. `state_path` 在配置文件 */etc/neuron/neutron.conf* 中：`state_path = /opt/stack/data/neutron` （用于声明存放 neutron 状态文件的目录）
4. `report_interval` agent 向 server 报告状态的时间间隔。在 */etc/neuron/neutron.conf* 中：`report_interval = 30`
5. 以循环执行的方法（参考 oslo_service之loopingcall 文章）启动 agent 状态的报告方法 `_report_state`。

### `def _report_state(self)`

关于 `agent_state` 变量：

在 `__init__` 方法中被初始化为：

```
        self.agent_state = {
            'binary': 'neutron-dhcp-agent',
            'host': host,
            'availability_zone': self.conf.AGENT.availability_zone,
            'topic': topics.DHCP_AGENT,
            'configurations': {
                'notifies_port_ready': True,
                'dhcp_driver': self.conf.dhcp_driver,
                'dhcp_lease_duration': self.conf.dhcp_lease_duration,
                'log_agent_heartbeats': self.conf.AGENT.log_agent_heartbeats},
            'start_flag': True,
            'agent_type': constants.AGENT_TYPE_DHCP}
```

* 配置选项讲解：
 1. `dhcp_lease_duration` 配置用来设定 dhcp ip 租赁的过期时间。在 */etc/neutron/neutron.conf* 中被设置：`dhcp_lease_duration = 86400`。
 2. `log_agent_heartbeats`：**作用：**   。在 */etc/neutron/neutron.conf* 中被设置：`log_agent_heartbeats = false`。
 3. `start_flag`：这个属性只会在第一次发送 agent state 的时候出现，表示这个时候，agent 刚刚启动

1. 调用 `cache.get_state()` 获取当前 dhcp 管理的 network、subnet、port 的数量
2. 通过 RPC 调用 Server 端（`AgentExtRpcCallback`）的 `report_state` 方法，上报当前 dhcp agent 的数据，并获取 dhcp agent 的状态（`new`、`alive`、`revived`）。
3. 若是 RPC 返回的 agent 的状态为 `revived`，则调用 `schedule_resync` 方法标记所有的网络都需要进行同步
4. dhcp agent 刚启动时 `start_flag` 为 `True`，这时会 `run` 方法。同时取消 `start_flag` 的标志。

### ``



## `class DhcpAgent(manager.Manager)`

`target = oslo_messaging.Target(version='1.0')`

### `def __init__(self, host=None, conf=None)`

```
    def __init__(self, host=None, conf=None):
        super(DhcpAgent, self).__init__(host=host)
        self.needs_resync_reasons = collections.defaultdict(list)
        self.dhcp_ready_ports = set()
        self.conf = conf or cfg.CONF
        self.cache = NetworkCache()
        self.dhcp_driver_cls = importutils.import_class(self.conf.dhcp_driver)
        self.plugin_rpc = DhcpPluginApi(topics.PLUGIN, self.conf.host)
        # create dhcp dir to store dhcp info
        dhcp_dir = os.path.dirname("/%s/dhcp/" % self.conf.state_path)
        utils.ensure_dir(dhcp_dir)
        self.dhcp_version = self.dhcp_driver_cls.check_version()
        self._populate_networks_cache()
        # keep track of mappings between networks and routers for
        # metadata processing
        self._metadata_routers = {}  # {network_id: router_id}
        self._process_monitor = external_process.ProcessMonitor(
            config=self.conf,
            resource_type='dhcp')
```

1. 初始化各种属性
2. 调用 `_populate_networks_cache` 将之前已经处理过的 network 资源保存在 cache 
3. 


### `def _populate_networks_cache(self)`

1. 调用 `dhcp_driver_cls.existing_dhcp_networks` 来读取该 dhcp agent 之前已经处理过的 network 资源
2. 以 `NetModel` 来描述上一步获取网络资源（`id`） `net = dhcp.NetModel({"id": net_id, "subnets": [], "ports": []})`并保存在 cache 中

### `def schedule_resync(self, reason, network_id=None)`

`reason`：进行同步操作的原因
`network_id`：对那个网络进行同步操作，若此参数为 None，则会对所有的网络进行重新同步

```
   def schedule_resync(self, reason, network_id=None):
        """Schedule a resync for a given network and reason. If no network is
        specified, resync all networks.
        """
        self.needs_resync_reasons[network_id].append(reason)
```

### `def run(self)`

```
    def run(self):
        """Activate the DHCP agent."""
        self.periodic_resync()
        self.start_ready_ports_loop()
```

### `def periodic_resync(self)`

启动一个绿色线程，运行 `_periodic_resync_helper` 方法

### `def _periodic_resync_helper(self)`

这是个死循环的方法，会一直执行。

`resync_interval`：当 `needs_resync_reasons` 标记有需要重新同步的网络资源时，需要与 neutron 进行重新同步的操作。这个数据就是检查需要重新同步操作的时间间隔。在 `dhcp_agent.ini` 中定义：`resync_interval = 5`。

作用：若有需要进行同步操作的 network，则调用 `sync_state` 方法

### `def start_ready_ports_loop(self)`

启动一个绿色线程池去调用 `_dhcp_ready_ports_loop` 方法

### `def _dhcp_ready_ports_loop(self)`

这是个死循环的方法，会一直执行。

作用：针对 `dhcp_ready_ports` 调用 rpc server 的 `dhcp_ready_on_ports` 方法。

### `def init_host(self)`

```
    def init_host(self):
        self.sync_state()
```

在 dhcp agent 刚启动的时候，会调用这个方法。这个方法用来同步 dhcp agent 这次启动之前已经处理过的 network 的信息

### `def sync_state(self, networks=None)`

`num_sync_threads`：执行同步操作时的绿色线程池的大小。在 `dhcp_agent.ini` 中定义：`num_sync_threads = 4`。

1. 创建一个绿色线程池，线程池的大小与 `num_sync_threads` 一致。
2. 获取该 dhcp agent 缓存的网络资源信息
3. 通过 RPC 调用 Server 端的 `get_active_networks_info` 方法，获取与当前 dhcp agent 绑定的网络信息（包括子网和端口）
4. 若是缓存的网络信息与通过RPC调用获取的网络信息不一致，调用 `disable_dhcp_helper` 方法处理那些不在 neutron server 端数据库中记录网络
5. 调用 `safe_configure_dhcp_for_network` 处理那些需要同步的网络（若 networks 为空，则意味着对所有的网络都执行一遍配置操作）
6. 将重新配置完成的网络的端口放入 `dhcp_ready_ports` 中，在 `_dhcp_ready_ports_loop` 中进行处理

### `def disable_dhcp_helper(self, network_id)`

在 dhcp agent 中去除 network_id 声明的网络

1. 调用 `disable_isolated_metadata_proxy` 杀死为这个网络提供 metadata 服务的进程
2. 调用 dhcp driver 的 `disable` 方法

### `def disable_isolated_metadata_proxy(self, network)`

调用 `MetadataDriver.destroy_monitored_metadata_proxy` 杀死为这个网络提供 metadata 服务的进程

### `def call_driver(self, action, network, **action_kwargs)`

1. 初始化 dhcp driver 实例（**从这里我们看出，dhcp agent 的 driver 实例不是一直存在的，而是用到的时候就被初始化，然后使用。并且每个 driver 实例只负责一个网络**）
2. 调用 dhcp driver 的 action 方法

### `def update_isolated_metadata_proxy(self, network)`

* 调用 `dhcp_driver_cls.should_enable_metadata` 来判断应该为 network 孵化或者杀死 metadata proxy process。
 1. 若是应该孵化，则调用 `enable_isolated_metadata_proxy` 方法
 2. 若是应该杀死，则调用 `disable_isolated_metadata_proxy` 方法

### `def enable_isolated_metadata_proxy(self, network)`

调用 `MetadataDriver.spawn_monitored_metadata_proxy` 启动一个 neutron-ns-metadata-porxy 进程，并对其进行监测。

### `def safe_configure_dhcp_for_network(self, network)`

调用 `configure_dhcp_for_network` 实现，并处理了可能发生的异常

### `def configure_dhcp_for_network(self, network)`

1. 调用 dhcp driver 的 `enable` 方法
2. 调用 `update_isolated_metadata_proxy` 处理与该网络相关的 neutron-ns-metadata-porxy 进程
3. 在 `dhcp_ready_ports` 记录被 dhcp agent 完成处理的 port 资源

### `def refresh_dhcp_helper(self, network_id)`

该 network 中的 subnet 可能发生了变化（删除、新建），该方法就是处理这些更新的情况

### `def _is_port_on_this_agent(self, port)`

判断该 port 是否是为该 dhcp agent 提供监听服务的 port。

dhcp agent 会为每个 network 建立一个 namespace，在这个 namespace 中建立一个网卡监听 dhcp 请求。

**下面介绍的几个方法是 RPC 方法，也就是 neutron-server 将会调用这些方法。**

### `def network_create_end(self, context, payload)`

调用 `enable_dhcp_helper` 方法来处理该 network

### `def network_update_end(self, context, payload)`

1. 若该网络由禁用到激活，则调用 `enable_dhcp_helper` 方法处理
2. 若该网络由激活到禁用，则调用 `disable_dhcp_helper` 方法处理

### `def network_delete_end(self, context, payload)`

调用 `disable_dhcp_helper` 处理该网络

### `def subnet_update_end(self, context, payload)`

调用 `refresh_dhcp_helper` 来处理该网络

### `subnet_create_end = subnet_update_end`

### `def subnet_delete_end(self, context, payload)`

调用 `refresh_dhcp_helper` 进行处理

### `def port_update_end(self, context, payload)`

某一网络的 port 发生了更新操作，若该 port 是为该 dhcp agent 提供监听的端口，则会调用 dhcp driver 的 `restart` 方法；否则的话会调用 dhcp driver 的 `reload_allocations` 方法

### `port_create_end = port_update_end`

### `def port_delete_end(self, context, payload)`

某一网络的 port 发生了删除操作，若该 port 是为该 dhcp agent 提供监听的端口，则会调用 dhcp driver 的 `disabl` 方法；否则的话会调用 dhcp driver 的 `reload_allocations` 方法