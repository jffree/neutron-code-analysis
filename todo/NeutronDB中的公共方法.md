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

### `def register_model_query_hook(cls, model, name, query_hook, filter_hook,                                  result_filters=None)`

注册用于 Query 的钩子方法。

### `_dict_extend_functions`

保存扩展资源属性的 API

### `def register_dict_extend_funcs(cls, resource, funcs)`

注册额外的方法到 `_dict_extend_functions` 中。

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

### `def _apply_filters_to_query(self, query, model, filters, context=None)`

在已经拥有的 query 的基础上，根据 filters 的条件和使用的数据库模型 model，进行过滤操作。返回过滤后的 query 对象。

### `_get_collection_query`

```
def _get_collection_query(self, context, model, filters=None,
                              sorts=None, limit=None, marker_obj=None,
                              page_reverse=False):
```

构造一个资源集合的查询，就是一次性在数据库中查询匹配多个资源。
可进行排序和分页操作。

### `_get_collection`

```
    def _get_collection(self, context, model, dict_func, filters=None,
                        fields=None, sorts=None, limit=None, marker_obj=None,
                        page_reverse=False)
```

1. 调用 `_get_collection_query` 进行批量查询
2. 调用传递过来的 `dict_func` 将批量查询的结果转换为字典格式
3. 调用 `attributes.populate_project_info` 填充 `tenant_id` 和 `project_id` 属性。

### `def _get_collection_count(self, context, model, filters=None)`

获取数据库批量查询的结果的数量。

### `def _get_by_id(self, context, model, id)`

通过 id 获取数据库中的记录



















