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










