# neutron db 中的公共方法

neutron db 中使用的公共方法在 *neutron/db/mixin.py* 中被封装成了一个类：`CommonDbMixin`

我们来慢慢的看这个类

## `class CommonDbMixin(object)`

### `_model_query_hooks`

plugin 和 实现 extension 的 minxin 类会在这个字典中注册一些钩子方法

这些钩子分为 `query`、`filter`、`result_filters` 三类

当用户对这个数据库进行查询操作时，会首先调用 `query` 对应的钩子函数创建一个数据库查询对象，紧接着会调用 `filter` 对象创建一个数据库过滤对象。

这样子其实是创建了基本的查询操作，然后用户可以在这个基本查询的基础上尝试其他的查询。

`register_model_query_hook` 和 `unregister_query_hook` 方法专门来对这个字典进行操作。

### `def _fields(self, resource, fields)`

根据用户请求中包含的 `fields` 来过滤要返回的 `resource` 信息。

### `def _apply_dict_extend_functions(self, resource_type,                                    response, db_object)`

有些 extension 指定 plugin 含有一些特定的方法，这个方法就是调用针对这个资源类型（`resource_type`）的特定方法来根据数据库查询结果（`db_object`）处理已经构造的相应（`response`）。

### `def model_query_scope(context, model)`

判断当前的请求是否具有 `admin` 或者 `advsvc` 权限，有的话返回 false
没有的话，且当前当前的请求中不包含 `tenant_id` 也返回 false
这个方法是用来限定数据库查询范围的，对非管理员用户来说，只能访问符合其 `tenant_id` 的数据库。

### `def _model_query(self, context, model)`

利用 `_model_query_hooks` 里面的钩子方法做基本的查询和过滤操作。