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
6. `extra_filter_names`，用户可以那这个选项进行数据的查询，但是这个选项却不可以用到数据库的查询中，在进行数据库查询前，需要将这个查询选项删除掉。
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

### `def db_obj(self)`

返回该 object 是从哪个数据库记录转化来的，也就是返回 `_captured_db_model` 属性

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

### `def get_objects(cls, context, _pager=None, validate_filters=True, **kwargs)`

获取数据库中的多个对象。

1. _pager 用于分页和排序
2. validate_filters 为 true 时，检测过滤参数（`**kwargs`）是否正确

1. 调用 `validate_filters` 验证数据库过滤参数
2. 调用 `modify_fields_to_db` 将 object 的属性转化为数据库认识的属性
3. 调用数据库方法 `obj_db_api.get_objects` 获取查询结果
4. 调用 `_load_object` 将所有查询到的结果转化为 versioned object

### `def modify_fields_to_db(cls, fields)`

将对象形式的 fields 转化为数据库形式的 fields，主要和 `fields_need_translation` 属性有关

### `def is_accessible(cls, context, db_obj)`

根据 context 判断是否有权限访问这个数据库记录（`db_obj`）

### `def filter_to_str(value)`

将 value 转化为字符串格式

```
    @staticmethod
    def filter_to_str(value):
        if isinstance(value, list):
            return [str(val) for val in value]
        return str(value)
```

### `def create(self)`

创建数据库记录

1. 调用 `_get_changed_persistent_fields` 获取被改变了的 field
2. 调用 `modify_fields_to_db` 将 object 的 field 转化为数据库识别的字段
3. 调用数据库方法 `obj_db_api.create_object` 创建数据库记录
4. 若数据库记录创建成功，则调用 `from_db_object`加载新创建的数据库记录的属性（也就是当前的 object 要和新的数据库记录关联起来了）。


### `def _get_changed_persistent_fields(self)`

获取被修改过的 field，在其中排除非本 object 对应数据库的字段

```
    def _get_changed_persistent_fields(self):
        fields = self.obj_get_changes()
        for field in self.synthetic_fields:
            if field in fields:
                del fields[field]
        return fields
```

### `def update(self)`

更新数据库记录

1. 调用 `_get_changed_persistent_fields` 获取被改变了的 field
2. 调用 `_validate_changed_fields` 验证是否存在不允许更新的字段
3. 调用 `_get_composite_keys` 获取 primary key，并根据 primary key 获取数据库记录
4. 调用 `modify_fields_to_db` 将 object 的 field 转化为数据库的字段
5. 调用 `obj_db_api.update_object` 更新数据库记录

 
### `def _validate_changed_fields(self, fields)`

类属性 `fields_no_update` 存储着 object （数据库）不允许更新的字段

该方法就是检测 fields 中是否含有了不允许更新的字段

### `def _get_composite_keys(self)`

获取 primary key

```
    def _get_composite_keys(self):
        keys = {}
        for key in self.primary_keys:
            keys[key] = getattr(self, key)
        return keys
```

### `def update_fields(self, obj_data, reset_changes=False)`

更新 object 的 fields，而不是更新 object 对应数据库的数据。

若 `reset_changes` 为 True，则调用 `obj_reset_changes` 方法清空 object 的更新记录。

```
    def update_fields(self, obj_data, reset_changes=False):
        if reset_changes:
            self.obj_reset_changes()
        for k, v in obj_data.items():
            if k not in self.fields_no_update:
                setattr(self, k, v)
```

### `def delete(self)`

1. 调用 `_get_composite_keys` 获取 primary keys
2. 调用 `modify_fields_to_db` 将 object field 转化为数据库字段
3. 调用 `obj_db_api.delete_object` 删除这条数据库记录
4. 设 `_captured_db_model` 属性为空

### `def count(cls, context, **kwargs)`

1. 调用 `validate_filters` 验证过滤参数 `**kwargs` 是否合法
2. 调用 `obj_db_api.count` 获取数据库查询到记录的数量

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

### `def validate_filters(cls, **kwargs)`

验证过滤参数是否正确

### `def add_extra_filter_name(cls, filter_name)`

在 `extra_filter_names` 属性中增加新的项目

### `def _synthetic_fields_items(self)`

```
    def _synthetic_fields_items(self):
        for field in self.synthetic_fields:
            if field in self:
                yield field, getattr(self, field)
```

### `def is_synthetic(cls, field)`

```
    @classmethod
    def is_synthetic(cls, field):
        return field in cls.synthetic_fields
```

### `def is_object_field(cls, field)`

```
    @classmethod
    def is_object_field(cls, field):
        return (isinstance(cls.fields[field], obj_fields.ListOfObjectsField) or
                isinstance(cls.fields[field], obj_fields.ObjectField))
```

### `def clean_obj_from_primitive(cls, primitive, context=None)`

1. 调用 `obj_from_primitive` 从 primitive 中构造一个 object
2. 调用 `obj_reset_changes` 清除新的 object 中的 changed_field

### `def to_dict(self)`

以字典的形式来展示 object 的 primitive 数据。

这个方法要比 `obj_to_primitive` 方法获取的 primitive 数据少一些属性，只相当于其中的 `data`。

## 其他方法

### `def _detach_db_obj(func)`

从 session 中分离（删除）db_obj，这是个装饰器方法

### `def get_object_class_by_model(model)`

从数据模型 model 获取 object 的最新类

### `def get_updatable_fields(cls, fields)`

获取 object （`cls`）中可更新的 field。

### `def register_filter_hook_on_model(model, filter_name)`

1. 调用 `get_object_class_by_model` 根据模型获取 object 类
2. 调用 object 的 `add_extra_filter_name` 增加额外的过滤选项



