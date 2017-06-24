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

### `def obj_to_primitive(self, target_version=None, version_manifest=None)`

以 primitive 形式的数据来描述 object，并且允许 object 的版本转化。

1. 不允许低版本向高版本转化
2. 获取 object 所有 field 的 primitive 类型的数据
3. 调用 `obj_make_compatible_from_manifest`

### `def obj_make_compatible_from_manifest(self, primitive, target_version, version_manifest)`

1. 设置 `_obj_version_manifest` 属性（`version_manifest`）
2. 调用 `obj_make_compatible` 方法
3. 删除 `_obj_version_manifest` 属性


```
    def obj_make_compatible_from_manifest(self, primitive, target_version,
                                          version_manifest):
        self._obj_version_manifest = version_manifest
        try:
            return self.obj_make_compatible(primitive, target_version)
        finally:
            delattr(self, '_obj_version_manifest')
```

### `def obj_make_compatible(self, primitive, target_version)`

```
    def obj_make_compatible(self, primitive, target_version)
        for key, field in self.fields.items():
            if not isinstance(field, (obj_fields.ObjectField,
                                      obj_fields.ListOfObjectsField)):
                continue
            if not self.obj_attr_is_set(key):
                continue
            self._obj_make_obj_compatible(primitive, target_version, key)
```

主要是调用 `_obj_make_obj_compatible` 对单个的 field 来实现版本转换

这里需要转换的 field 是 `ObjectField` 或者 `ListOfObjectsField`，也就是与本 object 有关的其他 object（我们成为子 object）。

### `def _obj_make_obj_compatible(self, primitive, target_version, field)`

```
    def _obj_make_obj_compatible(self, primitive, target_version, field):
        relationship_map = self._obj_relationship_for(field, target_version)
        if not relationship_map:
            # NOTE(danms): This means the field was not specified in the
            # version manifest from the client, so it must not want this
            # field, so skip.
            return

        try:
            _get_subobject_version(target_version,
                                   relationship_map,
                                   lambda ver: _do_subobject_backport(
                                       ver, self, field, primitive))
        except exception.TargetBeforeSubobjectExistedException:
            # Subobject did not exist, so delete it from the primitive
            del primitive[field]
```

### `def _obj_relationship_for(self, field, target_version)`

获得当前 object 与 `field` 所代表的子 object 的版本关系。

**请参考：** `obj_relationships` 属性的说明。

## 其他方法

### `def _get_attrname(name)`

```
def _get_attrname(name):
    """Return the mangled name of the attribute's underlying storage."""
    return '_obj_' + name
```

### `def _get_subobject_version(tgt_version, relationships, backport_func)`

* `tgt_version`：父对象的目标版本
* `relationships`：父对象与子对象的版本关系
* `backport_func`：获取子目标版本后，调用该方法处理子目标版本

请参考 `obj_relationships` 属性的说明。

### `def _do_subobject_backport(to_version, parent, field, primitive)`

* `to_version`：子目标版本
* `parent`：父对象实例
* `field`：子对象在父对象中的 field
* `primitive`：父对象所有的 primitive 类型的 field

1. 获取子对象实例
2. 从父对象中获取 `manifest`