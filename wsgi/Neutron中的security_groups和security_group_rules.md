# Neutron 中的 security_groups 和 security_group_rules

类似于 availablity_zone，security_groups 和 security_group_rules 的实现也是通过 extension 来实现的。

*neutron/extensions/securitygroup.py*

这个模块中定义了实现为 security_groups 和 security_group_rules 提供接口的抽象基类：`class SecurityGroupPluginBase(object)`

*neutron/db/security_groups_db.py* 是真正的实现

这个模块就一个类 `SecurityGroupDbMixin`，下面我们来详细讲一下这个类。

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
3. 调用 `_check_for_duplicate_rules` 检查是否已经有相同的 rule 注册
4. 检查通过后创建一条 `SecurityGroupRule` 数据库记录，并添加到回话中
5. 调用 `registry.notify` 发送通知消息 `PRECOMMIT_CREATE`
6. 调用 `_make_security_group_rule_dict` 将创建的数据库对象解析成字典格式
7. 再次调用 `registry.notify` 发送创建完成的通知 `AFTER_CREATE`
8. 返回第6步转化的字典

### `def _validate_security_group_rule(self, context, security_group_rule)`

1. 调用 `_validate_port_range` 检查端口范围是否合适
2. 调用 `_validate_ip_prefix` 检查 `remote_ip_prefix` 参数是否合法
3. 调用 `_validate_ethertype_and_protocol` 检查 `ethertype ` 和 `protocol ` 参数是否合法
4. `remote_ip_prefix` 和 `remote_group_id` 只能声明一个
5. 调用 `get_security_group` 检查 `remote_group_id` 指定的 security_group 是否存在
6. 调用 `get_security_group` 检查用户是否有权限在 `security_group_id` 指定的 security_group 上增加 rule

### `def _check_for_duplicate_rules(self, context, security_group_rules)`

1. 调用 `_rules_equal` 判断客户端发出的请求中是否包含和相同的 rule
2. 调用 `_check_for_duplicate_rules_in_db` 判断数据库中是否存在了相同的 rule

### `def _check_for_duplicate_rules_in_db(self, context, security_group_rule)`

1. 调用 `_make_security_group_rule_filter_dict` 将客户端发送过来的请求数据转化为字典类型，用来构造数据了的 filter 选项。
2. 调用 `get_security_group_rules` 获取符合过滤条件的 security_group_rules
3. 在排除 `id` 字段的情况下进行将客户端的数据与数据库的查询数据进行对比，查看该条规则是否已经存在

### `def _get_ip_proto_number(self, protocol)`

获取协议名称对应的协议号

### `_get_ip_proto_name_and_num`

获取协议名称以及协议号。

### `def delete_security_group_rule(self, context, id)`

测试命令

```
curl -s -X DELETE http://172.16.100.106:9696/v2.0/security-group-rules/090e66b6-fafe-4fd4-bb54-23effddc242c -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151'
```

1. 调用 `registry.notify` 发送准备删除的通知 `BEFORE_DELETE`
2. 查询 `SecurityGroupRule` 数据库，获取与 `id` 相同的记录
3. 调用 `registry.notify` 发送准备删除的通知 `PRECOMMIT_DELETE`
4. 执行数据库的删除动作
5. 调用 `registry.notify` 发送准备删除的通知 `AFTER_DELETE`

### `get_security_group_rules`

```
def get_security_group_rules(self, context, filters=None, fields=None,
                                 sorts=None, limit=None, marker=None,
                                 page_reverse=False)
```

测试命令：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-group-rules -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151'
```

1. 调用 `_get_marker_obj` 获取用于分页作用
2. 调用 `common_db_mixin.CommonDbMixin._get_collection` 来获取结果

### `def create_security_group_rule_bulk(self, context, security_group_rules)`

批量创建 security_group_rule

直接调用 `self._create_bulk`

`def _create_bulk(self, resource, context, request_items)` 方法是在 *neutron/db/db_base_plugin_v2.py* 中的 `NeutronDbPluginV2`中实现。这个方法也是循环的调用 `create_security_group_rule`

### `def create_security_group_rule_bulk_native(self, context,                                               security_group_rules)`

批量创建 security_group_rule 的本地（本类）实现

1. 利用 sqlalchemy 的 `scoped_session` 来管理 session [sqlalchemy 学习（二）scoped session](http://blog.csdn.net/hedan2013/article/details/54865144)
2. 调用 `_validate_security_group_rules` 检查用户发送过来的数据的有效性
3. 调用 `get_security_group` 获取这个 rule 的所属组
4. 调用 `_check_for_duplicate_rules` 检查是否有已经注册的 rule
5. 循环调用 `_create_security_group_rule` 实现 rule 的批量创建

### `def _rules_equal(self, rule1, rule2)`

判断 rule1 和 rule 除 `id` 属性外，其余属性是否一致

### `def get_security_group(self, context, id, fields=None, tenant_id=None)`

测试命令：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-groups/e021afac-aa12-47c9-acec-5e2e1721a625 -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151' | jq
```

1. 调用 `_get_security_group` 根据 `id` 获取 `SecurityGroup` 数据库中的记录
2. 调用 `_make_security_group_dict` 将数据库查询记录转化为字典形式
3. 调用 `get_security_group_rules` 获取该 security_group 下的 rules 记录，并保存于刚才的字典中。
4. 返回结果

### `def delete_security_group(self, context, id)`

测试命令：

```
curl -s -X DELETE http://172.16.100.106:9696//v2.0/security-groups/e021afac-aa12-47c9-acec-5e2e1721a625 -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151'
```

1. 调用 `_get_port_security_group_bindings` 查看是否有端口绑定在这个安全组上
2. 默认的安全组非 admin 不可移除
3. 调用 `registry.notify` 发送 `BEFORE_DELETE` 的消息
4. 调用 `registry.notify` 发送 `PRECOMMIT_DELETE` 的消息
5. 执行数据库的删除操作
6. 调用 `registry.notify` 发送 `AFTER_DELETE` 的消息

### `def _get_port_security_group_bindings(self, context,                                          filters=None, fields=None)`

查询 `SecurityGroupPortBinding` 数据库查询与某个 security_group 绑定的 port信息

### `def update_security_group(self, context, id, security_group)`

1. 调用 `registry.notify` 发送 `BEFORE_UPDATE` 的消息
2. 非 admin 用户不能对默认的安全组执行更新操作
3. 调用 `registry.notify` 发送 `PRECOMMIT_UPDATE` 的消息
4. 执行数据库的更新操作
5. 调用 `registry.notify` 发送 `AFTER_UPDATE` 的消息

### `def create_security_group(self, context, security_group, default_sg=False)`

* 用户端发送的数据示例：

```
{
    "security_group": {
        "name": "new-webservers",
        "description": "security group for webservers"
    }
}
```

1. 调用 `registry.notify` 发送 `BEFORE_CREATE` 的消息
2. 调用 `_ensure_default_security_group` 先确保有一个默认的安全组存在
3. 创建一条 `SecurityGroup` 数据库记录
4. 若是创建默认的安全组的情况下会创建一条 `DefaultSecurityGroup` 数据库记录
5. 若是创建默认的安全组的情况下回创建一条 `SecurityGroupRule` 数据库记录做默认规则
6. 创建一条 `SecurityGroupRule` 数据库记录做本安全组的默认规则
7. 调用 `registry.notify` 发送 `PRECOMMIT_CREATE` 的消息
8. 调用 `_make_security_group_dict` 将数据库记录转化为字典形式
9. 调用 `registry.notify` 发送 `AFTER_CREATE` 的消息
10. 返回字典信息

### `def _ensure_default_security_group(self, context, tenant_id)`

确保该 tenant 下有一个默认的安全组。若是没有的话则会创建一个

### `get_security_groups`

```
def get_security_groups(self, context, filters=None, fields=None,                                                                               
                            sorts=None, limit=None,
                            marker=None, page_reverse=False, default_sg=False)
```

测试命令：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/security-groups -H 'Content-Type: application/json' -H 'X-Auth-Token: 5f4e0cc153f64653bac02dab107e2151'
```

1. 根据分页需求调用 `_get_marker_obj` 
2. 调用 `_get_collection` 获取信息并返回

### `def get_security_groups_count(self, context, filters=None)`

调用  `_get_collection_count` 获取数据库查询的结果个数

### `def update_security_group_on_port(self, context, id, port, original_port, updated_port)`

**更新 port 上的安全组，这个方法会在 ml2 的 `update_port` 中调用**

1. 调用 `utils.compare_elements` 对比用户发送过来的 port 的安全组信息和 port 之前的安全组信息是否相同。若相同的话，则不会执行安全组的更新动作；不同的话，则更新 port 绑定的安全组。
2. 若需要更新安全组，则调用 `_get_security_groups_on_port` 获取需要更新的安全组的信息
3. 调用 `_delete_port_security_group_bindings` 删除 `SecurityGroupPortBingding` 数据库中的关于此 port_id 的记录
4. 调用 `_process_port_create_security_group` 创建 `SecurityGroupPortBingding` 数据库记录

### `def _get_security_groups_on_port(self, context, port)`

根据用户发送过来的 port 资源的相关数据，获取用户感兴趣的安全组数据。

### `def _create_port_security_group_binding(self, context, port_id,                                                                                 security_group_id)`

根据 port_id 和 security_group_id 创建一条 `SecurityGroupPortBingding` 数据库记录。

### `def _get_security_groups_on_port(self, context, port)`

当用户没有为 port 资源绑定安全组时，调用此方法为 port 资源绑定一个默认的安全组。

### `def _check_update_has_security_groups(self, port)`

检查该 port（用户传递过来的数据） 是否分配了安全组来绑定。

### `def _check_update_deletes_security_groups(self, port)`

与 `_check_update_has_security_groups` 有细微的差别，该方法检查port（用户传递过来的数据） 有安全组选项，但是为空或者 `validators.is_attr_set` 检测失败