# neutron 之 api_common 模块

*neutron/api/api_common.py*

## `def list_args(request, arg)`

从 `request.GET` 的参数列表中获取与 `arg` 一致的参数。

## `def get_filters(request, attr_info, skips=None)`

提取 request.GET 的参数，调用 `get_filters_from_dict`

## `def get_filters_from_dict(data, attr_info, skips=None)`

从 data 中构建过滤列表（用户想要获取的资源属性）。

## 有关排序的类

`class SortingHelper(object)`

`class SortingEmulatedHelper(SortingHelper)`

`class SortingNativeHelper(SortingHelper)`

`class NoSortingHelper(SortingHelper)`

## `def get_sorts(request, attr_info)`

提取客户端请求中的排序键值对

## 有关分页的帮助类

`class PaginationHelper(object)`

`class PaginationEmulatedHelper(PaginationHelper)`

`class PaginationNativeHelper(PaginationEmulatedHelper)`

`class NoPaginationHelper(PaginationHelper)`

