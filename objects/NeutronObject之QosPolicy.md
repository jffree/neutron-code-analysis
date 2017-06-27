# Neutron objects 之 QosPolicy

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