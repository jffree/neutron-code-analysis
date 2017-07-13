# dhcp agent 的启动

在 devstack 的环境中，我们可以看到启动 dhcp agent 的命令如下：

```
/usr/bin/neutron-dhcp-agent --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/dhcp_agent.ini & echo $! >/opt/stack/status/stack/q-dhcp.pid; fg || echo "q-dhcp failed to start" | tee "/opt/stack/status/stack/q-dhcp.failure"
```

## neutron-dhcp-agent

这个 neutron-dhcp-agent 是如何来的呢？我们看 neutron 的 setup.cfg 文件：

```
[entry_points]
...
    neutron-dhcp-agent = neutron.cmd.eventlet.agents.dhcp:main
```

根据上面的信息，我们在 _neutron/cmd/eventlet/agents/dhcp.py_ 中看到：

```
from neutron.agent import dhcp_agent


def main():                                                                                                                                                            
    dhcp_agent.main()
```

## dhcp agent 的启动

_neutron/agent/dhcp\_agent.py_

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

1. 调用 `register_options` 注册 dhcp agent 的相关配置选项
2. 调用 `common_config.init(sys.argv[1:])` 从配置文件中读取配置（这里说明：配置文件中的选项会覆盖默认选项）
3. 调用 `config.setup_logging` 设置 log 
4. 调用 `neutron_service.Service.create` 创建服务
5. 调用 `service.launch` 启动服务

## dhcp agent 之 RPC

这个 RPC 客户端与服务端主要是用于实现 neutron-server 与 neutron-dhcp-agent 端进行网络、子网、端口创建的交互

* Server 端：dhcp agent 启动后既是以一个 RPC Server 来启动的。
 * endpoint 为：`DhcpAgentWithStateReport`（也被称为 manager）
 * topic 为：`dhcp_agent`
 * host 为：`cfg.CONF.host`
* Client 端：在 ml2 中的 `_start_rpc_notifiers` 方法中被初始化（`DhcpAgentNotifyAPI`）

## dhcp agent state 之 RPC

这个 RPC 客户端与服务端主要是用于实现 neutron-dhcp-agent 端向 neutron-server 端报告自己 agent 的状态

* Server 端：
 * endpoint 为： `neutron.db.agents_db.AgentExtRpcCallback`，在 `ml2._setup_rpc` 方法中被初始化
 * topic 为：`q-reports-plugin`
 * host 为：`cfg.CONF.host`
* Client 端：`PluginReportStateAPI`，在 `DhcpAgentWithStateReport.__init__` 方法中被初始化
 * topic 为：`q-reports-plugin`





