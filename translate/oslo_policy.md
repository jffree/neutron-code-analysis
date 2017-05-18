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





























