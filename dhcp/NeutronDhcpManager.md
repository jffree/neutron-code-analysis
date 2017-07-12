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

1. dhcp agent service 创建的时候，没有声明 host，所以采用配置文件中声明的 host：`cfg.CONF.host`
2. `dhcp_driver_cls` 在配置文件 */etc/neutron/dhcp_agent.ini* 中为：`dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq`
3. `state_path` 在配置文件 */etc/neuron/neutron.conf* 中：`state_path = /opt/stack/data/neutron` （用于声明存放 neutron 状态文件的目录）
`




## `class DhcpAgent(manager.Manager)`

`target = oslo_messaging.Target(version='1.0')`



## `class NetworkCache(object)`

用于在 dhcp agent 端存储网络的相关信息

### `def __init__(self)`

```
    def __init__(self):
        self.cache = {}
        self.subnet_lookup = {}
        self.port_lookup = {}
        self.deleted_ports = set()
```


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