# neutron 中的 policy 方法

neutron 中策略检查相关的方法

实现：*neutron/policy.py*

在 neutron 中有一个唯一的全局变量：`_ENFORCER`，这个全局变量是所有 policy 的负责人。

## `reset()`

清除 `_ENFORCER` 中的 policy

## `init(conf=cfg.CONF, policy_file=None)`

初始化 `_ENFORCER`，并加载 */etc/neutron/policy.json* 中的 policy。

## `refresh(policy_file=None)`

对之前的 `_ENFORCER` 进行 `reset` 操作后再重新初始化一个 `_ENFORCER`。

## `get_resource_and_action(action, pluralized=None)`

根据 action 获取资源集合名称，并且判断是否要对资源的子属性进行 policy 检查。

`get` 和 `delete` 类的方法是无需进行子属性检查的，但是其他方法（`list`、`create`、`update`）都需要进行子属性检查，因为使用这些方法对资源进行访问时会提交数据。
 
## `set_rules(policies, overwrite=True)`

重置 `_ENFORCER` 中的 rules，直接覆盖 `_ENFORCER` 原有的 rules。

## `_is_attribute_explicitly_set(attribute_name, resource, target, action)`

判断用户提交的数据（`target`）中是否对某一属性（`attribute_name`）设定了明确的参数。

## `_should_validate_sub_attributes(attribute, sub_attr)`

判断某一资源的属性下面是否有子属性（这个属性是否有 `validate`选项），是否该对此子属性进行检查。

若子属性以 `type:dict` 开始，且用户提交的资源访问数据可遍历，则对此子属性进行检查。

## `_build_subattr_match_rule(attr_name, attr, action, target)`

若某个属性下的子属性需要进行检查，则对这个子属性构造检查的规则。

## `_build_match_rule(action, target, pluralized)`

根据 `action`（请对对应的plugin需要执行的动作）、`target`（请求传递过来的数据（填充完的））、`pluralized` 资源的负数名（集合名）来构造一个检查规则（`RuleCheck` 类型或者 `AndCheck` 类型）。 

* 这个检查规则是这样子的：

 1. 首先是构造这个动作的检查规则（比如说 `create_network`）
 2. 接着是构造对要访问的资源的属性的检查规则（比如说 `networks` 资源下的 `name`、`subnet`、`admin_state_up`等（这些都保存在 `RESOURCE_ATTRIBUTE_MAP`）中） 
 3. 最后是构造针对子属性的检查规则
 4. 将所有的规则合并到一个总规则中（一个单独的 `RuleCheck` 或一个合并的 `AndCheck`）

**由这里可以看出，检查规则是实时构造的，是根据客户端发出的具体请求来构造的，每次请求都会构造一遍。**

## `_process_rules_list(rules, match_rule)`

构造一个 `RuleCheck` 类型的列表，将 `AndCheck` 类型的检查规则拆开成一个个的 `RuleCheck` 加入到 这个列表中。

## `_prepare_check(context, action, target, pluralized)`

检查前的准备工作。

## `log_rule_list(match_rule)`

在需要的情况下将所有的检查规则打印到 log 中。

## `check(context, action, target, plugin=None, might_not_exist=False, pluralized=None)`

执行规则检查：

1. admin 用户永远为 True
2. 若 `_ENFORCER.rules` 不包含对 action 的检查且 `might_not_exist` 为真时，返回为 True
3. 利用 `_ENFORCER.enforce` 来执行检查，不引发异常，并将检查结果返回

这个方法主要用于 GET 的请求方法中

## `enforce(context, action, target, plugin=None, pluralized=None)`

执行规则检查：

1. admin 用户永远为 True
2. 直接利用 `_ENFORCER.enforce` 来执行检查，出错会引发异常（但会处理），返回检查结果。

## `check_is_admin(context)`

根据请求的 context 验证当前请求是否具有 admin 权限

这个方法是在构造 Context 时调用的。

## `check_is_advsvc(context)`

根据请求的 context 验证当前请求是否具有 advsvc 权限

这个方法是在构造 Context 时调用的。

# 策略检查的相关调试：

## 测试命令（以非admin用户运行）：

*以 admin 用户运行的话只能调试 admin 的认证*

```

```

## policy.json 中关于 create_network 的部分：

```
    "create_network": "",
    "get_network": "rule:admin_or_owner or rule:shared or rule:external or rule:context_is_advsvc",
    "get_network:router:external": "rule:regular_user",
    "get_network:segments": "rule:admin_only",
    "get_network:provider:network_type": "rule:admin_only",
    "get_network:provider:physical_network": "rule:admin_only",
    "get_network:provider:segmentation_id": "rule:admin_only",
    "get_network:queue_id": "rule:admin_only",
    "get_network_ip_availabilities": "rule:admin_only",
    "get_network_ip_availability": "rule:admin_only",
    "create_network:shared": "rule:admin_only",
    "create_network:router:external": "rule:admin_only",
    "create_network:is_default": "rule:admin_only",
    "create_network:segments": "rule:admin_only",
    "create_network:provider:network_type": "rule:admin_only",
    "create_network:provider:physical_network": "rule:admin_only",
    "create_network:provider:segmentation_id": "rule:admin_only",
    "update_network": "rule:admin_or_owner",
    "update_network:segments": "rule:admin_only",
    "update_network:shared": "rule:admin_only",
    "update_network:provider:network_type": "rule:admin_only",
    "update_network:provider:physical_network": "rule:admin_only",
    "update_network:provider:segmentation_id": "rule:admin_only",
    "update_network:router:external": "rule:admin_only",
    "delete_network": "rule:admin_or_owner",
```

1. 在 `polisy.init` 方法结尾处设置断点，查看所有的规则（都是以字典的形式保存）

```
(Pdb) p _ENFORCER.rules
```

2. 在 `base.Controller._create` 方法中设置断点（查看 `action`，`context`，`target`，`self._collection`）：

```
(Pdb) p request.context
(Pdb) p action
(Pdb) p item[self._resource]
(Pdb) p self._collection
```

3. 在 `policy.enforce` 方法中设置断点，查看为请求的构造的规则

```
(Pdb) p rule
(Pdb) p rule.rules
```

4. 在 `oslo_policy._checks.RuleCheck.__call__` 方法中设置断点

```
(Pdb) p self.match
(Pdb) p enforcer.rules[self.match]
```

剩下的救是循环进行规则检查的过程了。

# 提示

这里面涉及了很多 RBAC 策略实施的问题，请大家参考 oslo_policy 模块的 dev 文档。