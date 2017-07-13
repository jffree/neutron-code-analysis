# Neutron 中的 RPC Server 与 Client

## dhcp agent 之 RPC（一）

这个 RPC 客户端与服务端主要是用于实现 neutron-server 与 neutron-dhcp-agent 端进行网络、子网、端口创建的交互

* Server 端：dhcp agent 启动后既是以一个 RPC Server 来启动的。
 * endpoint 为：`DhcpAgentWithStateReport`（也被称为 manager）
 * topic 为：`dhcp_agent`
 * host 为：`cfg.CONF.host`
* Client 端：在 ml2 中的 `_start_rpc_notifiers` 方法中被初始化（`DhcpAgentNotifyAPI`）
 * topic 为：`dhcp_agent`
 * version 为：`1.0`

## dhcp agent 之 RPC（二）

dhcp agent 启动后，还会启动一个 RPC 的 Client 端，用来访问 neutron-server 的相关信息（主要是数据库）

* Server 端：`DhcpRpcCallback`（在 `ml2.start_rpc_listeners` 中初始化）
 * topic：`q-plugin`
 * host：`cfg.CONF.host`
 * namespace：`n_const.RPC_NAMESPACE_DHCP_PLUGIN`
 * version：`1.6`
* Client 端：`DhcpPluginApi` （在 `DhcpAgent.__init__` 方法中初始化）
 * topic：`q-plugin`
 * host：`cfg.CONF.host`
 * namespace：`n_const.RPC_NAMESPACE_DHCP_PLUGIN`
 * version：`1.0`


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

## Consumer Resource Version

* Server : `ResourcesPushToServerRpcCallback` 在 `ml2.start_rpc_listeners` 方法中被初始化
 * endpoint : `ResourcesPushToServerRpcCallback`  
 * topic : `q-server-resource-versions`
 * version : `1.0`
 * namespace : `RPC_NAMESPACE_RESOURCES` 
* Client : `ResourcesPushToServersRpcApi`  在 `AgentExtRpcCallback.__init__` 方法中被初始化
 * topic : `q-server-resource-versions`
 * version : `1.0`
 * namespace : `RPC_NAMESPACE_RESOURCES`