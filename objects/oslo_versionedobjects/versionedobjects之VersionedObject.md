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







## 其他方法

### `def _get_attrname(name)`

```
def _get_attrname(name):
    """Return the mangled name of the attribute's underlying storage."""
    return '_obj_' + name
```









