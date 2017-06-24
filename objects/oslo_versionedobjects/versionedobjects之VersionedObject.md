# versionedobjects 之 VersionedObject

这个子项目的文档太少了，直接看代码

*oslo_versionedobjects/base.py*

## `class VersionedObject(object)`

### `类属性`

```
indirection_api = None
VERSION = '1.0'
OBJ_SERIAL_NAMESPACE = 'versioned_object'
OBJ_PROJECT_NAMESPACE = 'versionedobjects'
fields = {}
obj_extra_fields = []
obj_relationships = {}  # 对象与对象的版本关系
```
### `def __init__(self, context=None, **kwargs)`

```
    def __init__(self, context=None, **kwargs):
        self._changed_fields = set()
        self._context = context
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
```

### `def obj_fields(self)`

```
@property
    def obj_fields(self):
        return list(self.fields.keys()) + self.obj_extra_fields
```

列出该对象的属性（把 `obj_extra_fields` 也视为对象的属性）

### `def obj_attr_is_set(self, attrname)`

判断该 object 是否已经有了这个属性（`attrname`）

若根本不存在这个属性，则引发异常。

若存在，但是没有设置这个属性，则返回 false

若存在，且已经设置了这个属性，则返回 True

### `def obj_set_defaults(self, *attrs)`

为对象的属性设置默认值。

1. 若是 `*attr` 为 None 的话，则从 `field` 获取带有默认值的属性
2. 若 `*attr` 不为 None 的话，则检查该属性是否有默认值
3. 检查这些属性是否已经设置，若没有设置，则为其设置默认值。

### `def obj_name(cls)`

类方法：

```
    @classmethod
    def obj_name(cls):
        return cls.__name__
```

### `def __repr__(self)`

### `def __contains__(self, name)`

```
    def __contains__(self, name):
        try:
            return self.obj_attr_is_set(name)
        except AttributeError:
            return False
```

### `def to_json_schema(cls)`

获取 json 格式的 schema

### `def _obj_primitive_key(cls, field)`

```
    @classmethod
    def _obj_primitive_key(cls, field):
        return '%s.%s' % (cls.OBJ_SERIAL_NAMESPACE, field)
```

### `def obj_clone(self)`

```
    def obj_clone(self):
        """Create a copy."""
        return copy.deepcopy(self)
```

### `def __deepcopy__(self, memo)`

1. 拷贝 context
2. 拷贝已经设置的 object 属性
3. 拷贝 changed_fields

### `def obj_context(self)`

属性方法，返回 context












## 其他方法

### `def _get_attrname(name)`

```
def _get_attrname(name):
    """Return the mangled name of the attribute's underlying storage."""
    return '_obj_' + name
```









