# oslo.policy

支持所有OpenStack服务中的RBAC策略实施的OpenStack库。

**RBAC：**基于角色的权限访问控制（Role-Based Access Control）

## 安装

```
$ pip install oslo.policy
```

```
$ mkvirtualenv oslo.policy
$ pip install oslo.policy
```

## oslo_policy package

### Submodules

#### oslo_policy.fixture module

##### `class oslo_policy.fixture.HttpCheckFixture(return_value=True)`

* Bases: `fixtures._fixtures.mockpatch.MockPatchObject`

有助于短路外部http call

#### oslo_policy.generator module

* `oslo_policy.generator.generate_policy(args=None)`
* `oslo_policy.generator.generate_sample(args=None)`
* `oslo_policy.generator.list_redundant(args=None)`
* `oslo_policy.generator.on_load_failure_callback(*args, **kwargs)`

#### oslo_policy.opts module

##### `oslo_policy.opts.list_opts()`

返回库中可用的oslo.config选项列表。

返回的列表包括可能在库的运行时注册的所有 `oslo.config` 选项。列表的每个元素都是一个元组。 第一个元素是组的名称，第二个元素中的元素列表将被注册到这个组中。组名为 `None` 对应于配置文件中的 `[DEFAULT]` 组。 通过  `oslo.config.opts` 命名空间下的 `oslo_messaging` 入口点也可以发现此功能。 这样做的目的是允许像 *Oslo* 示例配置文件生成器这样的工具来发现这个库暴露给用户的选项。

**return：**（group_name，opts）元组的列表

##### `oslo_policy.opts.set_defaults(conf, policy_file=None)`

设置配置变量的默认值。

覆盖选项的默认值。

* Parameters:	
 1. `conf (oslo.config.cfg.ConfigOpts)` – Configuration object, managed by the caller.
 2. `policy_file (unicode)` – 定义策略的基本文件名。

#### oslo_policy.policy module

实现通用 policy 的引擎

policy 的写法为：目标和相关规则

```
"<target>": <rule>
```

目标既是需要执行 policy 检查的服务。通常，目标是指API调用。

对于<rule>部分，请参阅 Policy Rule Expressions。

#### Policy Rule Expressions

策略规则可以用以下两种形式之一表示：一种是用新的策略语言编写的字符串，另一种是列表。字符串格式是首选，因为大多数人更容易理解。

在策略语言中，每个检查都指定为简单 `a：b` 类型的键值对，通过键值对来匹配正确的检查类。

* 用户角色格式：

```
role:admin
```

* 引用已经定义的 Rule：

```
rule:admin_required
```

* 针对 URL

```
http://my-url.org/check
```

*URL checking must return True to be valid*

* 用户属性：

```
project_id:%(target.project.id)s
```

*User attributes (obtained through the token): user_id, domain_id or project_id*

* String

```
<variable>:’xpto2035abc’
‘myproject’:<variable>
```

* Literals:

```
project_id:xpto2035abc
domain_id:20
True:%(user.enabled)s
```

可以使用连词操作符 `and` 和 `or`，允许在制定政策方面更具表现力。例如：

```
"role:admin or (project_id:%(project_id)s and role:projectadmin)"
```

策略语言还具有 `not` 运算符，允许更加丰富的策略规则：

```
"project_id:%(project_id)s and not role:dunce"
```

运算符优先级如下：

|PRECEDENCE|	TYPE|	EXPRESSION|
|--------- |:------:| -----------:|
|4	|Grouping	|(...)|
|3	|Logical NOT	|not ...|
|2	|Logical AND	|... and ...|
|1	|Logical OR	|... or ...|

具有较大优先级编号的运算符先于数字较小的其他数字。

在列表表单中，最内层列表中的每个检查与 `and` 操作符相结合，以指定所有指定的检查必须通过。然后将这些最内层列表与 `or` 操作符组合。作为示例，以列表表示形式表达请遵循以下规则：

```
[["role:admin"], ["project_id:%(project_id)s", "role:projectadmin"]]
```

最后提出两项特别政策检查; 策略检查 `@` 将始终接受访问，策略检查 `！` 将始终拒绝访问。 （请注意，如果规则是空列表（`[]`）或空字符串（`“”`），则相当于 `@` 策略检查。）其中， `！` 策略检查可能是最有用的 ，因为它允许明确禁用特定的规则。

##### Generic Checks

`generic` 检查用于对 API 调用一起发送的属性执行匹配检查。策略引擎可以使用这些属性（在表达式的右侧），请使用以下语法：

```
<some_attribute>:%(user.id)s
```

右侧的值是字符串，也可以使用常规Python字符串替换解析为字符串。可用的属性和值取决于使用 common 策略引擎的程序。

所有这些属性（与用户，API调用和上下文相关）可以相互对对方或常量进行检查。重要的是要注意，这些属性特定于执行策略执行的服务。

通用检查可用于对通过令牌获取的以下用户属性来执行策略检查：

* user_id
* domain_id or project_id (depending on the token scope)
* list of roles held for the given token scope

例如，对user_id的检查将被定义为：

```
user_id:<some_value>
```

与上个显示的示例一起，完整的通用检查将是：

```
user_id:%(user.id)s
```

还可以对表示凭证的其他属性执行检查。这通过向传递给 `enforce()` 方法的 `creds dict` 添加附加值来完成。

##### Special Checks

特殊检查允许比使用通用检查更多的灵活性。内置的特殊检查类型是 `role`, `rule`, and `http` 检查。


* Role Check

角色检查用于检查提供的凭据中是否存在特定角色。角色检查表示为：

```
"role:<role_name>"
```

* Rule Check

规则检查用于通过其名称引用另一个定义的规则。 这允许将常规检查定义为一次可重用规则，然后在其他规则中引用。 它还允许将一组检查定义为更具描述性的名称，以帮助策略的可读性。 规则检查表示为：

```
"rule:<rule_name>"
```

以下示例显示了定义为规则的角色检查，然后通过规则检查来使用：

```
"admin_required": "role:admin"
"<target>": "rule:admin_required"
```

* HTTP Check

http检查用于向远程服务器发出HTTP请求以确定检查结果。 将目标和凭据传递到远程服务器进行评估。 如果远程服务器返回True的响应，该操作将被授权。 http检查表示为：

```
"http:<target URI>"
```

预期目标URI包含字符串格式化关键字，其中关键字是目标字典中的键。来自目标的名称键用于构造URL的http检查的示例将被定义为：

```
"http://server.test/%(name)s"
```

* Registering New Special Checks

还可以使用 `register()` 函数注册附加的特殊检查类型。

以下类可用作自定义特殊检查类型的父类：

* `AndCheck`

* `NotCheck`

* `OrCheck`

* `RuleCheck`

##### Default Rule

可以定义默认规则，当正在检查的目标不存在规则时，该规则将被执行。 默认情况下，与默认规则名称相关联的规则将被用作默认规则。 通过将policy_default_rule配置设置设置为所需的规则名称，可以使用不同的规则名称作为默认规则。









## 参考

[Appendix A. The policy.json file](https://docs.openstack.org/kilo/config-reference/content/policy-json-file.html)

















