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

* dhcp agent 是以一个 service 的方式启动。
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

1. 调用 `cache.get_state()` 获取当前 dhcp 管理的 network、subnet、port 的数量
2. 


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














## `class DhcpPluginApi(object)`

在 dhcp agent 这边用作 RPC Client

### `def __init__(self, topic, host)`

```
    def __init__(self, topic, host):
        self.host = host
        target = oslo_messaging.Target(
                topic=topic,
                namespace=n_const.RPC_NAMESPACE_DHCP_PLUGIN,
                version='1.0')
        self.client = n_rpc.get_client(target)
```