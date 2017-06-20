# oslo_versionedobjects 之 VersionedObjectRegistry

*oslo_versionedobjects/base.py*

所有的 object 都应该利用 `oslo_versionedobjects.base.ObjectRegistry.register` 修饰器来进行注册。

## `class VersionedObjectRegistry(object)`

### 类属性

```
_registry = None
```

### `def objectify(cls, obj_cls)`

```
    @classmethod
    def objectify(cls, obj_cls):
        return cls.register_if(False)(obj_cls)
```

### `def register_if(cls, condition)`

```
    @classmethod
    def register_if(cls, condition):
        def wraps(obj_cls):
            if condition:
                obj_cls = cls.register(obj_cls)
            else:
                _make_class_properties(obj_cls)
            return obj_cls
        return wraps
```

本质上是对 `register` 方法和 `_make_class_properties` 方法的调用

### `def register(cls, obj_cls)`

```
    @classmethod
    def register(cls, obj_cls):
        registry = cls()
        registry._register_class(obj_cls)
        return obj_cls
```

1. 实例化 `VersionedObjectRegistry` 同时调用 `_register_class` 方法。

### `def __new__(cls, *args, **kwargs)`

`VersionedObjectRegistry` 使用 `__new__` 方法来进行实例化的

```
    def __new__(cls, *args, **kwargs):
        if not VersionedObjectRegistry._registry:
            VersionedObjectRegistry._registry = object.__new__(
                VersionedObjectRegistry, *args, **kwargs)
            VersionedObjectRegistry._registry._obj_classes = \
                collections.defaultdict(list)
        self = object.__new__(cls, *args, **kwargs)
        self._obj_classes = VersionedObjectRegistry._registry._obj_classes
        return self
```

这里的实现机制比较明显：

1. 保证类属性 `_registry` 的唯一性（也是一个 `VersionedObjectRegistry` 类实例），同时也保证了 `VersionedObjectRegistry._registry._obj_classes` 的唯一性
2. 构造了一个 `VersionedObjectRegistry` 实例，为了调用 `_register_class`
方法

### `def obj_classes(cls)`

```
    @classmethod
    def obj_classes(cls):
        registry = cls()
        return registry._obj_classes
```

返回 object 的映射

### `def _register_class(self, cls)` 

这个方法就是这个类的核心方法了

1. 定义内置方法：`def _vers_tuple(obj)` 将字符串类型的版本转化为元组形式（`'1.2.3'` --> `(1,2,3)`）
2. 调用 `_make_class_properties` 来为 object 的 field 的键来配置属性
3. 调用 `cls.obj_name`获取 object 的名称（也就是类名称）
4. 将 `{object_name:object}` 保存到 `VersionedObjectRegistry._registry._obj_classes` 中

### `def registration_hook(self, cls, index)`

```
    def registration_hook(self, cls, index):
        pass
```

## 其他方法

非 `VersionedObjectRegistry` 类方法的其他方法

### `def _make_class_properties(cls)`

1. 获取每个 object 的 `fields`
2. 获取所有父类的 `fields` 属性，并且更新到当前 object 的 `fields` 中
3. 判断所有的 `fields` 必须为 `Field` 的实例，同时为每个 field 的 `name` （键）增加 `get`、`set`、`delete`的方法。

```
setattr(cls, name, property(getter, setter, deleter))
```

## 总结（技巧）

1. 在 `__new__` 方法中，保证了类变量 `_registry` 的唯一性
2. 在 `register` 方法中，实例化一个类，在 `register` 调用完后，这个实例就会被释放。

**所以：**整个 neutron 中，只有一个 `VersionedObjectRegistry` 实例存在，那就是 `_registry`，且这个实例的 `_obj_classes` 属性是不断维护增长的。