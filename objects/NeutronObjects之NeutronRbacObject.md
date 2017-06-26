# Neutron objects 之 NeutronRbacObject

*neutron/objects/rbac_db.py*

这个 Objcet 有点复杂，我们看看是怎么实现的：

```
NeutronRbacObject = with_metaclass(RbacNeutronMetaclass, base.NeutronDbObject)
```

关于 `with_metaclass` 分析请看本篇文章的最后，从哪里我们可以知道 `NeutronRbacObject` 是没有意义的，有意义的是它的子类。

```
@obj_base.VersionedObjectRegistry.register
class QosPolicy(rbac_db.NeutronRbacObject)
```

这个 object 在 *neutron/objects/qos/policy.py* 中实现

## 元类：`class RbacNeutronMetaclass(type)`

### `def __new__(mcs, name, bases, dct)`

1. 调用 `validate_existing_attrs`


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