# Neutron 中的 security_groups 和 security_group_rules

类似于 availablity_zone，security_groups 和 security_group_rules 的实现也是通过 extension 来实现的。

*neutron/extensions/securitygroup.py*

这个模块中定义了实现为 security_groups 和 security_group_rules 提供接口的抽象基类：`class SecurityGroupPluginBase(object)`

*neutron/db/security_groups_db.py* 是真正的实现

这个模块就一个类 `SecurityGroupDbMixin`，下面我们来详细讲一下这个类。

## 测试命令

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-groups -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151'
```

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-group-rules -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151'
```

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-groups/e021afac-aa12-47c9-acec-5e2e1721a625 -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151' | jq
```

## `class SecurityGroupDbMixin(ext_sg.SecurityGroupPluginBase)`

### `def get_security_group_rule(self, context, id, fields=None)`

测试命令：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-group-rules/090e66b6-fafe-4fd4-bb54-23effddc242c -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151' | jq
```

1. 调用 `_get_security_group_rule` 访问 `SecurityGroupRule` 数据库，获取与 `security_group_rule_id` 相符合和记录。
2. 调用 `_make_security_group_rule_dict` 将数据库查询的结果构造成字典