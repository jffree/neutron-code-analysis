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

### ``