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

## dhcp agent server 的启动

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
 * namespace 为：`n_const.RPC_NAMESPACE_STATE`
* Client 端：`PluginReportStateAPI`，在 `DhcpAgentWithStateReport.__init__` 方法中被初始化
 * topic 为：`q-reports-plugin`
 * namespace 为：`n_const.RPC_NAMESPACE_STATE`

## dhcp agent 的启动流程

上面已经讲过，dhcp agent 是将 `class DhcpAgentWithStateReport(DhcpAgent)` 作为 rpc 的 server 端的 endpoint 来提供 dhcp 服务的，我们就以 manager 来称呼 `class DhcpAgentWithStateReport(DhcpAgent)` 的实例。

* 那么 dhcp agent 实际上的启动流程分为一下几个方面：
 1. manager 的初始化
 2. 调用 manager 的 `init_host` 方法
 3. 调用 manager 的 `after_start` 方法

我们下面一一分析：

### manager 的初始化

根据继承关系，manager 的初始化涉及到两个方法，分别是：`DhcpAgent.__init__` 和 `DhcpAgentWithStateReport.__init__`。

#### `DhcpAgent.__init__` 方法

1. 初始化一个 `NetworkCache` 的实例 `cache`，用于保存当前 dhcp agent 所维护的网络的相关信息；
2. 根据配置信息导入 `Dnsmasq` 类作为 dhcp agent 的 `dhcp_driver_cls`；
3. 通过实例化 `DhcpPluginApi` 为 `plugin_rpc` 来启动 RPC Client 端和 neutron-server 通信；
4. 调用 `_populate_networks_cache` 处理 dhcp agent 之前维护的 network 资源（将其加入到缓存中）；
5. 建立一个 `ProcessMonitor` 的实例 `_process_monitor` 用来监测与 dhcp agent 有关的外部进程；

#### `DhcpAgentWithStateReport.__init__`

1. 创建一个 `PluginReportStateAPI` 实例 `state_rpc` 用来 RPC Clinet 来向 neutron-server 汇报 dhcp agent 的状态
2. 创建一个 `FixedIntervalLoopingCall` 的实例来定时执行 `_report_state` 方法（该方法会向 neutron server 来汇报 dhcp agent 的状态）。
3. `_report_state` 在第一次运行时会调用 `run` 方法来激活 dhcp agent。

##### `DhcpAgent.run`

通过调用该方法会孵化两个绿色线程，分别执行 `_periodic_resync_helper` 和 `_dhcp_ready_ports_loop`，这个两个方法都是死循环执行的方法。

1. `_periodic_resync_helper` 方法，该方法用该判断是否有需要进行同步的操作（增加、删除）网络资源。这种同步操作通过调用 `sync_state` 方法来实现。
2. `_dhcp_ready_ports_loop` 方法，该方法会调用 RPC Server 端的 `dhcp_ready_on_ports` 方法来告诉 neutron-server 那些 port 已经在 dhcp agent 端处理好。

### manager 的 `init_host`

该方法的作用为：当 dhcp agent 启动完成后，会对所有该 dhcp agent 所负责的 network 进行一遍配置（`safe_configure_dhcp_for_network`）工作。
可以理解为，当 dhcp agent 完成启动后，初始化其负责的网络资源。

### manager 的 `after_start`

记录一个 log

## 参考

[配置 DHCP 服务 - 每天5分钟玩转 OpenStack（89）](http://www.cnblogs.com/CloudMan6/p/5887364.html)
[用 namspace 隔离 DHCP 服务 - 每天5分钟玩转 OpenStack（90）](http://www.cnblogs.com/CloudMan6/p/5894891.html)
[获取 dhcp IP 过程分析 - 每天5分钟玩转 OpenStack（91）](http://www.cnblogs.com/CloudMan6/p/5905996.html)
[Neutron 理解（5）：Neutron 是如何向 Nova 虚机分配固定IP地址的 （How Neutron Allocates Fixed IPs to Nova Instance）](http://www.cnblogs.com/sammyliu/p/4419195.html)
[nova boot代码流程分析(五)：VM启动从neutron-dhcp-agent获取IP与MAC](http://blog.csdn.net/gj19890923/article/details/51558598)
[Neutron分析（4）—— neutron-dhcp-agent](http://www.cnblogs.com/feisky/p/3848889.html)















