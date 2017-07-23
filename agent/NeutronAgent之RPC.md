# Neutron Agent 之 RPC

*neutron/agent/rpc.py*

## `class PluginReportStateAPI(object)`

该类为 RPC 的 Client 端，用于报告 agent 的状态。

对应的 Server 端为：`neutron.db.agents_db.AgentExtRpcCallback`

### `def __init__(self, topic)`

```
    def __init__(self, topic):
        target = oslo_messaging.Target(topic=topic, version='1.0',
                                       namespace=n_const.RPC_NAMESPACE_STATE)
        self.client = n_rpc.get_client(target)
```

初始化 RPC Client 端的操作

### `def report_state(self, context, agent_state, use_call=False)`

* 参数说明：
 1. context
 2. agent_state：agent 状态的详细数据（可参考 `DhcpAgentWithStateReport.agent_state`）
 3. use_call：若此变量为 True，则表示使用 call 方法；若此变量为 False，则表示使用 cast 方法

`rpc_response_timeout` 等待 RPC 响应的超时时间，该选项在 *neutron.conf* 中设定：`rpc_response_timeout = 60`

1. 进一步完善 agent state 的信息
2. 调用 Server 端的 `report_state` 方法

可以使用如下命令： `neutron agent show 4a3020c8-68e7-449c-9060-898fb150242c` 查看 agent 状态