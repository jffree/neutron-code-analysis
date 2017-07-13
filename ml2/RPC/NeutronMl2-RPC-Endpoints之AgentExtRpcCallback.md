# Neutron ML2 RPC endpoint 之 AgentExtRpcCallback

*neutron/db/agents_db.py*

Server 端的 endpoint，用于接收 Client 端的 agent_state 的调用

## `class AgentExtRpcCallback(object)`

```
    target = oslo_messaging.Target(version='1.1',
                                   namespace=n_const.RPC_NAMESPACE_STATE)
    START_TIME = timeutils.utcnow()
```

### `def __init__(self, plugin=None)`

```
    def __init__(self, plugin=None):
        super(AgentExtRpcCallback, self).__init__()
        self.plugin = plugin
        #TODO(ajo): fix the resources circular dependency issue by dynamically
        #           registering object types in the RPC callbacks api
        resources_rpc = importutils.import_module(
            'neutron.api.rpc.handlers.resources_rpc')
        # Initialize RPC api directed to other neutron-servers
        self.server_versions_rpc = resources_rpc.ResourcesPushToServersRpcApi()
```

### `def report_state(self, context, **kwargs)`

这个方法将会被 RPC Client 端调用（参考：`PluginReportStateAPI.report_state`）。

1. 调用 `_check_clock_sync_on_agent_start` 检查 agent 发送状态信息的时间与 Server 端收到状态信息的时间是否超过了 `agent_down_time`。（若是超过了，也只记录错误，但不引发异常）
2. 判断是否发送该信息时，Server 端还未启动，若是 Server 端还未启动则丢弃该信息
3. 获取 core plugin 的实例
4. 调用 core plugin 的 `create_or_update_agent` 方法（在 `AgentDbMixin` 中定义）来更新该 agent 在 `Agent` 数据库中的记录
5. 调用 `_update_local_agent_resource_versions` 处理 `resource_versions` 方面的信息（这个可以参考 `Open vSwitch agent`，`DHCP agent`、`L3 agent`以及`Metadata agent` 都没有这个信息）

### `def _check_clock_sync_on_agent_start(self, agent_state, agent_time)`

* 参数说明：
 * `agent_state`：agent 的状态数据
 * `agent_time`：agent 发送改状态的时间

`agent_down_time`：若在这个时间范围内，agent 没有回报自己的状态，则认为该 agent 已经挂掉。该配置位于 *neutron.conf* 中：`agent_down_time = 75`

判断 agent 发送改状态的时间与 RPC Server 端接收到的时间是否超过了 `agent_down_time` 的设定时间，若是超过改时间，则在 log 中记录错误

### `def _update_local_agent_resource_versions(self, context, agent_state)`

处理 agent state 中包含的 `resource_versions` 的信息

1. 若 agent state 中不包含这项记录，则直接退出
2. 若是包含 `resource_versions` 的记录，则调用 `CachedResourceConsumerTracker.update_versions` 来更新 consumer 是想用资源的追踪记录
3. 同时调用 `ResourcesPushToServersRpcApi.report_agent_resource_versions`