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

根据上面的信息，我们在 *neutron/cmd/eventlet/agents/dhcp.py* 中看到：

```
from neutron.agent import dhcp_agent
 
 
def main():                                                                                                                                                            
    dhcp_agent.main()
```

## dhcp agent 的启动

*neutron/agent/dhcp_agent.py*

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