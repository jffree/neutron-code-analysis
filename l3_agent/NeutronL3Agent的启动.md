# Neutron l3 agent 的启动

* 在 setup.cfg 文件中，我们可以看到：

```
[entry_points]
console_scripts =
    ...
    neutron-l3-agent = neutron.cmd.eventlet.agents.l3:main
```

* 在 *neutron/cmd/eventlet/agents/l3.py* 中： 

```
from neutron.agent import l3_agent


def main():
    l3_agent.main()
```

* 在 *neutron/agent/l3_agent.py* 中：

```
def main(manager='neutron.agent.l3.agent.L3NATAgentWithStateReport'):
    register_opts(cfg.CONF)
    common_config.init(sys.argv[1:])
    config.setup_logging()
    server = neutron_service.Service.create(
        binary='neutron-l3-agent',
        topic=topics.L3_AGENT,
        report_interval=cfg.CONF.AGENT.report_interval,
        manager=manager)
    service.launch(cfg.CONF, server).wait()
```

*l3 agent 的启动和 dhcp 服务的启动有点类似。*

* l3 agent 的启动做了如下初始化工作：
 1. 初始化 manager（`neutron.agent.l3.agent.L3NATAgentWithStateReport`）
 2. 调用 `manager.init_host` 方法（l3 agent 未做实现）
 3. 以 manager 为 RPC Server endpoint 启动监听
 4. 以间隔的时间去运行 `manager.periodic_tasks` 的方法（这个在 l3 agent 时不存在的，可以忽略）
 5. 运行 `manager.after_start` 方法