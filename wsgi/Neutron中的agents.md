# Neutron 中的 Agent

extension 模块：`neutron/extensions/agent.py`

wsgi 的实现模块、数据库模块：`neutron/db/agents_db.py`

我前面写过一篇文章 [neutron 中 AvailabilityZone 的实现](neutron中AvailabilityZone的实现.md)，其中说明了 `AvailabilityZone` 的查询也是在 `Agent` 数据库中进行的，今天我们就来看看这个 agents 的 WSGI 实现。

## `class AgentDbMixin(ext_agent.AgentPluginBase, AgentAvailabilityZoneMixin)`

* `ext_agent.AgentPluginBase` 是在个抽象类
* `AgentAvailabilityZoneMixin` 则是 `AvailabilityZone` 的 WSGI 实现

### `def get_agent(self, context, id, fields=None)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/agents/58ea7075-d9e6-4070-9e57-bbce22335f2c -H 'Content-Type: application/json' -H 'X-Auth-Token: cbc39c33b9334e54b3b561c451da1ee3' | jq
```

1. 调用 `_get_agent` 方法进行数据库查询
2. 调用 `_make_agent_dict` 将数据库查询结果转化为字典格式

### `def _get_agent(self, context, id)`

调用公共方法里面的 `_get_by_id` 根据 `id` 来获取 `Agent` 数据库记录。

### `def _make_agent_dict(self, agent, fields=None)`

将数据库查询结果转化为字典格式

### `def delete_agent(self, context, id)`

测试命令：

```
curl -s -X DELETE http://172.16.100.106:9696//v2.0/agents/58ea7075-d9e6-4070-9e57-bbce22335f2c -H 'Content-Type: application/json' -H 'X-Auth-Token: cbc39c33b9334e54b3b561c451da1ee3'
```

1. 调用 `_get_agent` 方法进行数据库查询
2. 调用回调系统中的 `registry.notify` 发出 `BEFORE_DELETE` 的事件通知
3. 删除数据库记录

### `def update_agent(self, context, id, agent)`

1. 调用 `_get_agent` 方法进行数据库查询
2. 更新数据库记录
3. 返回更新后的 agent 数据

### `def create_agent(self, context, agent)`

该方法依然是继承于 `AgentPluginBase`，注释中写的很明白，不允许 REST API 中有创建 agent 的操作。

```
    def create_agent(self, context, agent):
        """Create agent.

        This operation is not allow in REST API.
        @raise exceptions.BadRequest:
        """
        raise exceptions.BadRequest()
```

### `def get_agents(self, context, filters=None, fields=None)`

测试命令：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/agents -H 'Content-Type: application/json' -H 'X-Auth-Token: cbc39c33b9334e54b3b561c451da1ee3' | jq
```

1. 调用公共方法里面的 `_get_collection` 获取数据库记录
2. 过滤掉非 `alive` 的记录
3. 返回获取的数据

### `def get_enabled_agent_on_host(self, context, agent_type, host)`

获取某 host 上某一 agent_type 类型的 agent。

### `def is_agent_down(heart_beat_time)`

根据心跳检测时间（这里是 UTC 时间）判断 agent 是否挂掉了

### `def is_agent_considered_for_versions(agent_dict)`

### `def _get_agents_considered_for_versions(self)`

### `def get_agents_resource_versions(self, tracker)`

**这三个方法涉及到 RPC 中的资源版本管理，这个我们后面讲解**

### `def get_configuration_dict(self, agent_db)`

从 Agents 数据库查询结果中提取 `configurations` 的相关数据

### `def _get_dict(self, agent_db, dict_name, ignore_missing=False)`


从 Agents 数据库查询结果中提取 `dict_name` 的相关数据（get_configuration_dict就是调用的这个方法）

### `def create_or_update_agent(self, context, agent_state)`

创建或者更新 Agent 数据库记录

1. 从 `agent_state` 中构造 agent 的数据库配置
2. 调用 `_get_agent_by_type_and_host` 查询该 agent 是否已经存在
3. 调用 `_log_heartbeat` 记录心跳检测的日志
4. 已经存在的话则更新这个数据库
5. 不存在的话则创建数据库
6. 调用 Neutron 回调系统的 `registry.notify` 发送消息

### `def _get_agent_load(self, agent)`

**agents 数据库中 load ，具体还待研究**，可参考 `dhcp_load_type ` 的配置

### `def filter_hosts_with_network_access(self, context, network_id, candidate_hosts)`

在 `candidate_hosts` 过滤具有访问 `network_id` 网络权限的主机。