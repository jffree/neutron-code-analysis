# Neutron Objects 之 db 操作 API

*neutron/objects/db/api.py*

这个里面存放了一些操作数据库的方法。

## `def get_object(context, model, **kwargs)`

根据过滤条件 `**kwargs` 获取数据库 model 记录。

调用 `_get_filter_query` 实现

## `def _get_filter_query(context, model, **kwargs)`

1. 获取 ML2 plugin 的实例
2. 调用 `_kwargs_to_filters` 去做一下转换（过滤值都是列表的形式呈现）
3. 调用 `plugin._get_collection_query`进行数据库查询，这个方法是在 `CommonDbMixin` 类中实现的（请见我写的 **NeutronDB中的公共方法**）。

## `def _kwargs_to_filters(**kwargs)`

直接上源码吧，看的更清楚

```
def _kwargs_to_filters(**kwargs):
    return {k: v if isinstance(v, list) else [v]
            for k, v in kwargs.items()}
```

## `def count(context, model, **kwargs)`

调用 `_get_filter_query` 数据库查询结果的数量

## `def get_objects(context, model, _pager=None, **kwargs)`

思路与 `get_object` 一致，不过是调用 `plugin._get_collection` 来实现

## `def create_object(context, model, values)`

根据 value 创建一个数据库 model 的记录

## `def _safe_get_object(context, model, **kwargs)`

1. 调用 `get_object`
2. 若 `get_object` 的返回结果为 None 时，引发异常

## `def update_object(context, model, values, **kwargs)`

1. 调用 `_safe_get_object` 获取数据库记录
2. 利用 value 更新数据库记录
3. 保存更新后的数据库记录

## `def delete_object(context, model, **kwargs)`

1. 调用 `_safe_get_object` 获取数据库记录
2. 删除数据库记录