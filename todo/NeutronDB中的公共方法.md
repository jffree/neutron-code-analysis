# neutron db 中的公共方法

neutron db 中使用的公共方法在 *neutron/db/mixin.py* 中被封装成了一个类：`CommonDbMixin`

我们来慢慢的看这个类

## `class CommonDbMixin(object)`

### `def _fields(self, resource, fields)`

根据用户请求中包含的 `fields` 来过滤要返回的 `resource` 信息。

### `def _apply_dict_extend_functions(self, resource_type,                                    response, db_object)`

有些 extension 指定 plugin 含有一些特定的方法，这个方法就是调用针对这个资源类型（`resource_type`）的特定方法来根据数据库查询结果（`db_object`）处理已经构造的相应（`response`）。