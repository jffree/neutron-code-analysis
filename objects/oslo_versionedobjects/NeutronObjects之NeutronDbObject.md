# Neutron objects 之 NeutronDbObject

*neutron/objects/base.py*

```
@six.add_metaclass(DeclarativeObject)
class NeutronDbObject(NeutronObject)
```

## 一些重要的属性：

1. `fields` 对应 object 模型里面的字段
2. `obj_extra_fields`，非模型字段的额外属性，提供这些数据有利于更容易的使用该对象
3. `fields_no_update` 更新操作时不需要操作的属性
4. `fields_need_translation` 属性在 object 里面的名称与在 db 里面名称的对应关系（`{'field_name_in_object': 'field_name_in_db'}`）
5. `unique_keys` 代表着数据库中独一无二的字段
6. `extra_filter_names`
7. `synthetic_fields` 标记着与当前 object 有关系的其他 object（也就是数据库中的一对一、一对多、多对多的关系 `orm.relationship`）。
8. `_changed_fields`，若对该 object 的某一属性设置过值，则会在 `_changed_fields` 属性中进行记录，调用 `obj_reset_changes` 会清除记录。 


## `class DeclarativeObject(abc.ABCMeta)`

这是 `NeutronDbObject` 的元类，我们看这个里面实现的功能

1. 若是 `NeutronDbObject` 或者其子类的 `fields` 中含有 `project_id`，则将 `tenant_id` 加入到 `obj_extra_fields` 中，同时为改类设置 `tenant_id` 的属性方法（**这里有个技巧，请看源码**）。
2. 取类以及其基类的 `primary_keys` 和 `obj_extra_fields` 数据，将其更新到 设置为 `fields_no_update` 属性。
3. 若是类中设置了 `db_model` 属性，则从对应的数据模型中提取出 `unique_keys`，然后使用 `_detach_db_obj` 方法修饰类的 `create` 和 `update` 方法。
4. 若是该类有 `has_standard_attributes` 属性且 `has_standard_attributes` 方法调用为真的话，则调用 `standardattributes.add_standard_attributes` 来更新类的 `fields`
5. 设定 `extra_filter_names` 属性

## `class NeutronDbObject(NeutronObject)`

这个类是 Neutron 中所有 object 的基类

### `def get_object(cls, context, **kwargs)`

类方法，从数据库中提取记录，并将其转化为versioned object。

`**kwargs` 是指数据库的过滤字段

1. 判断 `**kwargs` 是否在对象的 `primary_keys` 和 `unique_keys` 中。
2. 调用 `modify_fields_to_db` 实现对象名称到数据库名称的转换
3. 调用 `get_object` （objects 中的数据库操作方法） 获取数据库记录
4. 若存在数据库记录，则调用 `_load_object` 将数据库记录转化为 versioned object。

### `def modify_fields_to_db(cls, fields)`

类方法，实现对象名称到数据库字段名称的转换。（利用 `fields_need_translation` 属性）

### `def _load_object(cls, context, db_obj)`

1. 实例化此 Object
2. 调用 `from_db_object` 将数据库记录转化为 versioned object。
3. 从数据库会话中去掉实例（数据库中还是存在的）。

### `def from_db_object(self, db_obj)`

1. 调用 `modify_fields_from_db` 将数据库记录转化为 object 记录。
2. 调用 `load_synthetic_db_fields` 加载与当前对象有关系的 object（`synthetic_fields`）。
3. 设置 `_captured_db_model` 属性
4. 调用 `obj_reset_changes` 清除所有的被改变过属性的记录。

### `def modify_fields_from_db(cls, db_obj)`

提取数据库记录的数据，并根据 `fields_need_translation` 将数据库名称转换为 object 名称。

### `def load_synthetic_db_fields(self, db_obj=None)`

处理 `synthetic_fields` 中保存的该 object 与其他 object 的对应关系。

在这里会加载与该 object 有关的其他 object。

### `def obj_reset_changes(self, fields=None, recursive=False)`

清除 `_changed_fields` 的记录。

1. 若设置了 `recursive` 为 True，则对于该 object 有关系的 object 也执行 `obj_reset_changes` 操作。
2. 若 `fields` 不为空，则之删除 `fields` 记录。
3. 若 `fields` 为空，则删除所有记录。

### `def obj_get_changes(self)`

调用 `obj_what_changed` 获取当前 object 被改变的属性。
返回被改变的属性，及其该属性的当前值。

### `def obj_what_changed(self)`

返回当前 object 被修改的属性名称，若是与该 object 相关的 object 的属性也被修改过的话，则相关 object 的名称也要加入到其中。




## `NeutronObject`

```
@six.add_metaclass(abc.ABCMeta)
class NeutronObject(obj_base.VersionedObject,
                    obj_base.VersionedObjectDictCompat,
                    obj_base.ComparableVersionedObject)
```

### 类属性

```
    synthetic_fields = []
    extra_filter_names = set()
```

### `def __init__(self, context=None, **kwargs)`

```
    def __init__(self, context=None, **kwargs):
        super(NeutronObject, self).__init__(context, **kwargs)
        self.obj_set_defaults()
```

主要是调用 `obj_set_defaults` 为对象的属性设置默认值。

## 其他方法

### `def _detach_db_obj(func)`

从 session 中分离（删除）db_obj，这是个装饰器方法












