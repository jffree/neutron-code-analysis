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


### `def create_security_group_rule(self, context, security_group_rule)`

测试数据：

```
{
    "security_group_rule": {
        "direction": "ingress",
        "port_range_min": "80",
        "ethertype": "IPv4",
        "port_range_max": "80",
        "protocol": "tcp",
        "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
        "security_group_id": "a7734e61-b545-452d-a3cd-0189cbd9747a"
    }
}
```

该方法直接调用了 `_create_security_group_rule`

### `def _create_security_group_rule(self, context, security_group_rule,                                    validate=True)`

1. 调用 `_validate_security_group_rule` 检验传递过来的数据的正确性
2. 调用 `registry.notify` 发送通知消息
3. 调用 `_check_for_duplicate_rules_in_db` 检查是否有冲入的 rule 注册


### `def _validate_security_group_rule(self, context, security_group_rule)`

1. 调用 `_validate_port_range` 检查端口范围是否合适
2. 调用 `_validate_ip_prefix` 检查 `remote_ip_prefix` 参数是否合法
3. 调用 `_validate_ethertype_and_protocol` 检查 `ethertype ` 和 `protocol ` 参数是否合法
4. `remote_ip_prefix` 和 `remote_group_id` 只能声明一个
5. 调用 `get_security_group` 检查 `remote_group_id` 指定的 security_group 是否存在
6. 调用 `get_security_group` 检查用户是否有权限在 `security_group_id` 指定的 security_group 上增加 rule

### `def _check_for_duplicate_rules_in_db(self, context, security_group_rule)`

1. 调用 `_make_security_group_rule_filter_dict` 将客户端发送过来的请求数据转化为字典类型，用来构造数据了的 filter 选项。
2. 





