# Nuetron Api Handlers 之 resources_rpc

*nuetron/api/handlers/resources_rpc.py*

## 本模块中的 RPC Server and Client

* Server : `ResourcesPushToServerRpcCallback` 在 `ml2.start_rpc_listeners` 方法中被初始化
 * endpoint : `ResourcesPushToServerRpcCallback`  
 * topic : `q-server-resource-versions`
 * version : `1.0`
 * namespace : `RPC_NAMESPACE_RESOURCES` 
* Client : `ResourcesPushToServersRpcApi`  在 `AgentExtRpcCallback.__init__` 方法中被初始化
 * topic : `q-server-resource-versions`
 * version : `1.0`
 * namespace : `RPC_NAMESPACE_RESOURCES` 

## `class ResourcesPushToServersRpcApi(object)`


### `def __init__(self)`

```
    def __init__(self):
        target = oslo_messaging.Target(
            topic=topics.SERVER_RESOURCE_VERSIONS, version='1.0',
            namespace=constants.RPC_NAMESPACE_RESOURCES)
        self.client = n_rpc.get_client(target)
```

### `def report_agent_resource_versions(self, context, agent_type, agent_host, version_map)`

调用位置 `AgentExtRpcCallback._update_local_agent_resource_versions`

以广播的形式调用 `cast` 方法来调用 RPC Server 端的 `report_agent_resource_versions` 方法

## `class ResourcesPushToServerRpcCallback(object)`

```
    target = oslo_messaging.Target(
        version='1.0', namespace=constants.RPC_NAMESPACE_RESOURCES)
```

### `def report_agent_resource_versions(self, context, agent_type, agent_host, version_map)`


```
    def report_agent_resource_versions(self, context, agent_type, agent_host,
                                       version_map):
        consumer_id = version_manager.AgentConsumer(agent_type=agent_type,
                                                    host=agent_host)
        version_manager.update_versions(consumer_id, version_map)
```

**疑问：**

擦，这个不是同 `AgentExtRpcCallback._update_local_agent_resource_versions` 方法中 `version_manager.update_versions` 的调用一模一样吗？

好吧，在 `AgentExtRpcCallback._update_local_agent_resource_versions` 有这么一句话：*report other neutron-servers about this quickly*

难道还会有多个 neutron-server 同时运行？