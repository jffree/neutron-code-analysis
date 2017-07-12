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