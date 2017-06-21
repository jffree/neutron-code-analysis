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


## `class DeclarativeObject(abc.ABCMeta)`

这是 `NeutronDbObject` 的元类，我们看这个里面实现的功能

1. 若是 `NeutronDbObject` 或者其子类的 `fields` 中含有 `project_id`，则将 `tenant_id` 加入到 `obj_extra_fields` 中，同时为改类设置 `tenant_id` 的属性方法（**这里有个技巧，请看源码**）。
2. 取类以及其基类的 `primary_keys` 和 `obj_extra_fields` 数据，将其更新到 设置为 `fields_no_update` 属性。
3. 若是类中设置了 `db_model` 属性，则从对应的数据模型中提取出 `unique_keys`，然后使用 `_detach_db_obj` 方法修饰类的 `create` 和 `update` 方法。
4. 若是该类有 `has_standard_attributes` 属性且 `has_standard_attributes` 方法调用为真的话，则调用 `standardattributes.add_standard_attributes` 来更新类的 `fields`
5. 设定 `extra_filter_names` 属性

















## 其他方法

### `def _detach_db_obj(func)`

从 session 中分离（删除）db_obj，这是个装饰器方法












