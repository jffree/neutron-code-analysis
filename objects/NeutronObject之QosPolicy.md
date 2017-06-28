# Neutron objects 之 QosPolicy

**导读：**Neutron 中有 network 和 qos 两种资源实现了 rbac 管理。对于这两种资源，若其 `shared` 属性为 True，则其可以被所有的租户访问。那么其对应的 rbac 规则中，`target_tenant` 应该为 `*`。

**注意：**

`rules` 是 qos policy object 的子 object，共有三种（在 *neutron/objects/qos/rules.py* 中实现）。

这三种子 object 是在 qos policy object 的不同版本加入的，所有 qos policy object 会有一个 `obj_make_compatible` 来做版本兼容。

**其他：**

*neutron/object/qos/policy.py*

```
@obj_base.VersionedObjectRegistry.register
class QosPolicy(rbac_db.NeutronRbacObject)
```

*neutron/objects/rbac_db.py*

这个 Objcet 有点复杂，我们看看是怎么实现的：

```
NeutronRbacObject = with_metaclass(RbacNeutronMetaclass, base.NeutronDbObject)
```

关于 `with_metaclass` 分析请看本篇文章的最后，从哪里我们可以知道 `NeutronRbacObject` 是没有意义的，有意义的是它的子类（`QosPolicy`）。

## 元类：`class RbacNeutronMetaclass(type)`

### `def __new__(mcs, name, bases, dct)`

1. 调用 `validate_existing_attrs`；
2. 调用 `update_synthetic_fields` 更新 object 的 `synthetic_fields` 属性；
3. 调用 `replace_class_methods_with_hooks` 更新 `create`、`update`、`to_dict` 方法；
4. 调用 type 实现新类（增加了基类 `RbacNeutronDbObjectMixin`）
5. 在新类的 `add_extra_filter_name` 增加 `shared` 选项
6. 调用 `subscribe_to_rbac_events` 对 rbac 资源的创建、删除、更新事件进行监听

### `def validate_existing_attrs(cls_name, dct)`

1. `fields` 中必须要含有 `shared`
2. 都必须要定义 `rbac_db_model`

### `def update_synthetic_fields(mcs, bases, dct)`

更新 `synthetic_fields`，将 `shared` 加入到其中。

若 dct 中没有 `synthetic_fields` ，则调用 `get_attribute` 获取。

### `def get_attribute(mcs, attribute_name, bases, dct)`

在 `dct` 中获取名为 `attribute_name` 的属性，若 dct 中没有，则调用 `_get_attribute` 从父类中获取。

### `def replace_class_methods_with_hooks(mcs, bases, dct)`

使用心得方法替换 dct （新类属性）中的 `create`、`update`、`to_dict`方法。

### `def subscribe_to_rbac_events(class_instance)`

订阅事件：

```
rbac-policy, before_delete, validate_rbac_policy_change
rbac-policy, before_update, validate_rbac_policy_change
rbac-policy, before_create, validate_rbac_policy_change
```

## `def _to_dict_hook(self, to_dict_orig)`

更新后的名为 `to_dict` 的方法

1. 先调用原版的 `to_dict` 方法
2. 调用 `is_shared_with_tenant` 判断该租户是否有权限访问该 object 权限，若是有权限则设定 `shared` 为 True，否则设定为 False

## `def _create_hook(self, orig_create)`

更新后的名为 `create` 的方法

1. 调用原版的 `create` 方法
2. 调用 `_create_post` 方法

## `def _create_post(self)`

如果新创建的 object 的 `shared` 属性为真，则调用 `attach_rbac` 方法来创建 rbac 的条目。

## `def _update_hook(self, update_orig)`

新版本的名为 `update` 的方法

1. 调用 `obj_get_changes` 获取被修改的 field
2. 调用原版的 update 方法
3. 调用 `_update_post` 方法

## `def _update_post(self, obj_changes)`

如果 `shared` 在 obj_changes 中，则调用 `update_shared` 方法
 
## `class RbacNeutronDbObjectMixin(rbac_db_mixin.RbacPluginMixin, base.NeutronDbObject)`

mixin 类，配合别的类完成功能

### `def get_bound_tenant_ids(cls, context, obj_id)`

抽象类方法，查找有多少个 tenant 用到了这个 object

### `def is_network_shared(context, rbac_entries)`

类方法，根据 rbac 的记录，判断该用户是否有权限访问这个网络

### `def is_accessible(cls, context, db_obj)`

判断该用户是否有权限访问这个 db object。

### `def is_shared_with_tenant(cls, context, obj_id, tenant_id)`

1. 提升 context 权限
2. 调用 `get_shared_with_tenant` 做实际的检查

### `def get_shared_with_tenant(context, rbac_db_model, obj_id, tenant_id)`

1. rbac_db_model：记录 rbac 规则的数据库
2. obj_id：待访问资源 object 的id（目前只有 network 或者 qos 实现了基于 rbac 的规则访问，所以，这里的 obj_id 可以是某个 network 的 id，或者某个 qos 的 id。）
3. tenant_id：准备访问该资源的租户的 id

直接调用 `common_db_mixin.model_query` 查询 `rbac_db_model` 查看该租户是否有访问这个资源的权利。

### `def attach_rbac(self, obj_id, tenant_id, target_tenant='*')`

调用 `RbacPluginMixin.create_rbac_policy` 来构造一个 rbac 数据库记录。

### `def update_shared(self, is_shared_new, obj_id)`

更新 shared field。

1. 获取 admin 权限
2. 调用 `obj_db_api.get_object` 查询 `shared` 为 true 时的 rbac 的数据库记录
3. 若 shared 属性与之前一致（未发生变化），则不作处理
4. 若 shared 由 false 变 true，则调用 `attach_rbac` 创建 rbac 的数据库记录
5. 若 shared 由 ture 变为 false，则调用删除数据库记录。

### `def validate_rbac_policy_change(cls, resource, event, trigger, context, object_type, policy, **kwargs)`

事件回调函数，用来验证对 rbac 策略的改动是否合法

1. 判断 rbac 对应的类型是否是当前 object 的类型。（因为 rbac 资源是一样的，但是 rbac 实现了对 qos 和 network 的策略访问，这个区分就是靠 `object_type` 来进行的，所以这里首先会判断 `object_type` 是否一致。）
2. 当对 rbac 资源进行创建和更新操作时，要求客户端具有相应的权限。
3. 这里只处理了 update 和 delete 操作，没有处理 create 操作。

```
{events.BEFORE_UPDATE: cls.validate_rbac_policy_update,
 events.BEFORE_DELETE: cls.validate_rbac_policy_delete}
```

### `def validate_rbac_policy_update(cls, resource, event, trigger, context, object_type, policy, **kwargs)`

 rbac 资源被更新前，调用此方法

当 rbac 的 `target_tenant` 发生改变时，可能会影响到一些租户对该资源的访问，这里会继续调用 `validate_rbac_policy_delete` 进行进一步的检测，看是否有租户依赖此 rbac 来访问资源。

### `def validate_rbac_policy_delete(cls, resource, event, trigger, context, object_type, policy, **kwargs)`

对 rbac 资源执行删除前，会调用此方法

1. 这里只处理 action 为 `models.ACCESS_SHARED` 的 rbac
2. 调用 `obj_db_api.get_object` 获取该 object 的数据库记录
3. 若 `db_obj.tenant_id == target_tenant`，对象本身所属的租户肯定有权限访问该对象，所以删除这样的 rbac 是无影响的
4. 调用 `_validate_rbac_policy_delete` 做进一步的检测

### `def _validate_rbac_policy_delete(cls, context, obj_id, target_tenant)`

检查删除某一个 rbac 记录是否会对 `target_tenant` 造成影响

* 参数说明：

1. obj_id：这是一个 object 的 id，那么这个 objcet 是指什么呢：qos policy 的 id。（仔细想一下：qospolicyrbacs 不就是针对 qospolicy 的 rbac 的策略控制吗，也就是谁可以修改这个 qospolicy）

1. 提升为 admin 权限
2. 调用 `get_bound_tenant_ids` 获取所有正在使用该 policy 的租户 id（`get_bound_tenant_ids` 是一个抽象方法，该方法在子类中实现。）
3. 调用 `_get_db_obj_rbac_entries` 获取 rbac 数据库中与该 policy 绑定且 action 为 `models.ACCESS_SHARED` 的 rbac 数据库记录
4. 若是删除掉该 rbac 记录后会影响别的租户的使用则引发异常

### `def _get_db_obj_rbac_entries(cls, context, rbac_obj_id, rbac_action)`

根据 `object_id` 和 `action` 针对 rbac 数据库做过滤查询

## `class QosPolicy(rbac_db.NeutronRbacObject)`

为了让大家更好的理解这一部分，我把测试方法和数据库记录贴出来给大家看看：

* 创建 network qos-policy、创建 qos policy rule、将 qos-policy 绑定 Network

```
neutron qos-policy-create --shared bw-limiter
neutron qos-bandwidth-limit-rule-create bw-limiter --max-kbps 3000 --max-burst-kbps 300
neutron net-update 534b42f8-f94c-4322-9958-2d1e4e2edd47 --qos-policy bw-limiter
```

* 数据库记录：

```
MariaDB [neutron]> select * from qos_policies;
+--------------------------------------+------------+----------------------------------+------------------+
| id                                   | name       | project_id                       | standard_attr_id |
+--------------------------------------+------------+----------------------------------+------------------+
| 963d9997-7e3c-4018-92e2-d81e1db9efcc | bw-limiter | d4edcc21aaca452dbc79e7a6056e53bb |               32 |
+--------------------------------------+------------+----------------------------------+------------------+
```

```
MariaDB [neutron]> select * from qos_bandwidth_limit_rules;
+--------------------------------------+--------------------------------------+----------+----------------+
| id                                   | qos_policy_id                        | max_kbps | max_burst_kbps |
+--------------------------------------+--------------------------------------+----------+----------------+
| 6714616e-cf73-4c6c-9158-cd0927247a2d | 963d9997-7e3c-4018-92e2-d81e1db9efcc |     3000 |            300 |
+--------------------------------------+--------------------------------------+----------+----------------+
```

```
MariaDB [neutron]> select * from qospolicyrbacs;                                                                                                                        
+--------------------------------------+----------------------------------+---------------+------------------+--------------------------------------+
| id                                   | project_id                       | target_tenant | action           | object_id                            |
+--------------------------------------+----------------------------------+---------------+------------------+--------------------------------------+
| 04945a9d-fac2-478c-80e7-87f32b68e96b | d4edcc21aaca452dbc79e7a6056e53bb | *             | access_as_shared | 963d9997-7e3c-4018-92e2-d81e1db9efcc |
+--------------------------------------+----------------------------------+---------------+------------------+--------------------------------------+
```

```
MariaDB [neutron]> select * from qos_network_policy_bindings;
+--------------------------------------+--------------------------------------+
| policy_id                            | network_id                           |
+--------------------------------------+--------------------------------------+
| 963d9997-7e3c-4018-92e2-d81e1db9efcc | 534b42f8-f94c-4322-9958-2d1e4e2edd47 |
+--------------------------------------+--------------------------------------+
```

### 类属性

```
    VERSION = '1.3'

    # required by RbacNeutronMetaclass
    rbac_db_model = QosPolicyRBAC
    db_model = qos_db_model.QosPolicy

    port_binding_model = qos_db_model.QosPortPolicyBinding
    network_binding_model = qos_db_model.QosNetworkPolicyBinding

    fields = {
        'id': obj_fields.UUIDField(),
        'tenant_id': obj_fields.StringField(),
        'name': obj_fields.StringField(),
        'shared': obj_fields.BooleanField(default=False),
        'rules': obj_fields.ListOfObjectsField('QosRule', subclasses=True),
    }

    fields_no_update = ['id', 'tenant_id']

    synthetic_fields = ['rules']

    binding_models = {'network': network_binding_model,
                      'port': port_binding_model}
```

### `def get_bound_tenant_ids(cls, context, policy_id)`

可能与 qos policy 有关的资源为：network、port。我们自然要根据 qos policy 的 id `policy_id` 看看有哪些资源和这个 qos policy 绑定，然后再根据资源查找到这个资源所属的租户，最后返回使用该 qos policy 的租户列表。

### `def obj_load_attr(self, attrname)`

只允许加载 `rules` 属性，调用 `reload_rules` 实现

### `def reload_rules(self)`

调用 `rule_obj_impl.get_rules` 加载所有与该 qos object 绑定的 rule。

为 object 设置 `rules` 属性

### `def get_rule_by_id(self, rule_id)`

通过 rule id 获取该 qos object 绑定的 rule

### `def get_object(cls, context, **kwargs)`

object 的关键方法，调用父类的 `get_object` 实现，同时为 object 增加 rules 属性

### `def get_objects(cls, context, _pager=None, validate_filters=True, **kwargs)`

类似于 `get_object` 方法

### `def get_network_policy(cls, context, network_id)`

根据 network 的 id，获取与之绑定的 qos policy 的 object

### `def get_port_policy(cls, context, port_id)`

根据 port 的 id，获取与之绑定的 qos policy 的 object

### `def create(self)`

这个方法会被 __metaclass__ 修饰

在父类的 `create` 方法上调用了 `reload_rules` 方法

### `def delete(self)`

该方法会被 `__metaclass__` 修饰

1. 检查该 qos policy object 是否被别的资源使用
2. 若未使用则调用父类的 `delete` 删除

### `def attach_network(self, network_id)`

将该 qos object 与一个 network 资源绑定

### `def attach_port(self, port_id)`

将该 qos object 与一个 port 资源绑定

### `def detach_network(self, network_id)`

将该 qos object 与一个 network 资源解除绑定

### `def detach_port(self, port_id)`

将该 qos object 与一个 port 资源解除绑定

### `def get_bound_networks(self)`

获取与该 qos policy object 绑定的 network

### `def get_bound_ports(self)`

获取与该 qos policy object 绑定的 port

### `def obj_make_compatible(self, primitive, target_version)`

父 object 与子 object 的版本兼容

## 黑魔法：`six.with_metaclass`

```
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
```

这个方法的代码就4行，但是里面有一个黑魔法，听我一一道来。

1. 我们都知道 `type` 可以用来定义一个类：

```
type(类名, 父类的元组（针对继承的情况，可以为空），包含属性的字典（名称和值）)
```

```
tc = type('temporary_class', (), {})
```

这样子，我们就定义了一个名为 `temporary_class` 的 `tc` 类，并且这个类没有父类，也没有自己的方法（除了一些默认方法，比如 `__init__` 之类）。

2. 那么关于 `__new__` 方法（不一定是 type 的 __new__ 方法）呢？我们通常会这么使用：

```
class A(object):
    def __new__(cls, *args, **kwargs)
        ....
```

`__new__` 方法会创建一个 `cls` 的实例，然后会调用 `cls` 的 `__init__` 方法来进行初始化.....

**其实，我认为最重要的一点是：`type.__new__` 方法是将 `cls` 与实例进行了关联。**

3. 那么，在 `six.with_metaclass` 方法中，我们就可以这么立即了：

`with_metaclass` 调用 `type.__init__` 创建了一个名为 `temporary_class` 的类，但是却将这个类设定为是由 `metaclass` 来创建的。

4. 如果我们继承了由 `six.with_metaclass` 创建的类，那么，我们自己的类也认为是由 `metaclass` 来创建的，自然会调用 `metaclass.__new__` 方法。
5. 仔细看一下 `metaclass.__new__` 方法，我们就会发现的它里面已经“偷梁换柱”了。 
