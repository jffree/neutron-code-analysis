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

### ``
















