# Neutron 中 WSGI Controller 分析

`Controller` 中有几个比较重要的方法，也是 WSGI 的接口：`index`、`show`、`create`、`delete`、`update`。

## 属性

### `_attr_info`

指的是资源的属性信息，保存于 *neutron/api/v2/attributes.py* 中的 `RESOURCE_ATTRIBUTE_MAP` 中（当然，某些 extension 会扩展相对于资源的属性）。

我们看一下 networks 的属性：

```
    NETWORKS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': NAME_MAX_LEN},
                 'default': '', 'is_visible': True},
        'subnets': {'allow_post': False, 'allow_put': False,
                    'default': [],
                    'is_visible': True},
        'admin_state_up': {'allow_post': True, 'allow_put': True,
                           'default': True,
                           'convert_to': lib_converters.convert_to_boolean,
                           'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': TENANT_ID_MAX_LEN},
                      'required_by_policy': True,
                      'is_visible': True},
        SHARED: {'allow_post': True,
                 'allow_put': True,
                 'default': False,
                 'convert_to': lib_converters.convert_to_boolean,
                 'is_visible': True,
                 'required_by_policy': True,
                 'enforce_policy': True},
    }
```

### `_policy_attrs`

被 policy 所需要的（`'required_by_policy': True`）资源属性列表

### `_notifier`

每个资源都有一个 `oslo_message.Notifier` 实例来发送一些通知信息。

```
self._notifier = n_rpc.get_notifier('network')
```

## `create`

1. 使用 `_notifier` 发送消息
2. 调用 `_create` 方法

## `_create`

1. 获取父类资源的id
2. 调用 `prepare_request_body` 方法进行检查工作
3. 获取 `_plugin` 中的实现的方法名称（例如：`create_network`）
4. policy 初始化 `policy.init()`
5. 调用 `_validate_network_tenant_ownership` 检查是否有权限访问依赖的 `network` 资源
6. 调用 `policy.enforce` 执行 policy 检查
7. 调用 `quota.QUOTAS.make_reservation` 为资源添加预定项。
8. 在 `do_create` 方法中调用支持此资源的 `plugin` 的真正方法去创建资源：
 1. 若是失败则会删除预定项，同时将该资源的 dirty 置位，提请改更新此资源的使用量；
 2. 成功则返回创建的结果。

9. 创建成功后会调用 `notify` 方法，
 1. 该方法会删除预定项，同时将该资源的 dirty 置位，提请改更新此资源的使用量。
 2. 调用 `self._notifier.info` 发送通知
 3. **调用消息回调体体系的方法 `registry.notify`，发送提示消息。**

## `prepare_request_body`

* 根据资源的 `_attr_info` 对用户请求的数据（body，消息体）做检查、填充默认数据的工作。

## `_validate_network_tenant_ownership(self, request, resource_item)`

* 因为 `subnet`、`port` 资源会依赖于 `network` 资源，若用户对 `subnet`、`port` 资源发出创建或更新（`create`）的方法请求时，则会检查用户是否有权限访问被依赖的 `network` 资源。
 
## `def _exclude_attributes_by_policy(self, context, data)`

创建资源成功时，会返回该资源的一系列属性，但是根据该资源的 `_attr_info` 有些属性对用户是不可见的，或者有些属性在 policy 中规定对用户是不可见的，那么则会在返回的属性信息中删除这些对用户不可见的属性，将剩余的属性信息返回。

该方法是收集对用户不可见的属性。

## `def _filter_attributes(self, context, data, fields_to_strip=None)`

该方法是删除对用户不可见的属性。

## `def _emulate_bulk_create(self, obj_creator, request, body, parent_id=None)`

模拟资源的批量创建，其实就是一个接一个的创建。

## `def _view(self, context, data, fields_to_strip=None)`

调用 `_exclude_attributes_by_policy` 与 `_filter_attributes` 返回用户可见的属性。

## `def index(self, request, **kwargs)`

* 初始化 policy
* 调用 `_items` 方法

* `list` 方法的测试命令

```
curl -s -X GET http://172.16.100.106:9696//v2.0/networks -H 'Content-Type: application/json' -H 'X-Auth-Token: 309c8fb973ba4b0bb64a6bafdc974d85'
```

```
curl -s -X GET 'http://172.16.100.106:9696//v2.0/networks?fields=id&fields=name' -H 'Content-Type: application/json' -H 'X-Auth-Token: 309c8fb973ba4b0bb64a6bafdc974d85' | jq
```

[Filtering and column selection](http://specs.openstack.org/openstack/neutron-specs/specs/api/networking_general_api_information.html#filtering-and-column-selection)

## `def _items(self, request, do_authz=False, parent_id=None)`

1. 获取 `GET` 中 `fields` 的参数列表（`fields` 表明客户端想要获得的信息，`fields`为空的话会获取全部的信息。）
2. 处理排序请求 `_get_sorting_helper`
3. 处理分页请求 `_get_pagination_helper`
4. 获取支持此资源的 plugin 的方法（例如：`list_networks`）
5. 调用 plugin 的方法，获取实际的响应
6. 对响应做 policy 检查
7. 调用 `_exclude_attributes_by_policy` 去除不能向用户展示的信息
8. 如果有分页请求的话，则会构造下一页的链接
9. 同步一下 `quotausages` 数据库的信息
10. 返回最终的请求响应。

## `def _get_sorting_helper(self, request)`

若在用户请求中有排序要求的话，则构造排序帮助类的实例。

## `def _get_pagination_helper(self, request)`

若在用户请求中有分页要求的话，则构造分页帮助类的实例。

## `def show(self, request, id, **kwargs)`

1. 获取 `GET` 中 `fields` 的参数列表（`fields` 表明客户端想要获得的信息，`fields`为空的话会获取全部的信息。）
2. 初始化 policy
3. 调用 `_item` 方法构造响应
3. 调用 `_view` 方法处理响应，去除不需要向客户端显示的信息。

* 测试方法

```
curl -s -X GET 'http://172.16.100.106:9696//v2.0/networks/2e4d0bc0-9b91-4be2-a174-c2fc7c60a8e3' -H 'Content-Type: application/json' -H 'X-Auth-Token: 5fd534f83fed466c93d84b47d421d18c' | jq
```

## `def _item(self, request, id, do_authz=False, field_list=None, parent_id=None)`

1. 获取 plugin 的方法
2. 调用 plugin 的方法
3. 做 policy 检查
4. 返回

## `def _view(self, context, data, fields_to_strip=None)`

去除 `data` 不需要向客户端显示的信息 `fields_to_strip`

## `def delete(self, request, id, **kwargs)`

1. 调用 `self._notifier.info` 发送通知消息
2. 调用 `self._delete` 执行真正的删除

## `def _delete(self, request, id, **kwargs)`

1. 获取 plugin 的方法（`delet_network`）
2. 初始化 policy
3. 调用 item，在不进行 policy 检查的情况获取资源情况
4. 针对 delete 动作做 policy 检查
5. 调用 plugin 的方法
6. 设置 `quotausages` 数据库的 `dirty` 位，提示该更新 quotausages
7. 调用 `self._notifier.info` 发送通知消息。
8. 调用 `registry.notify` 发送系统回调消息。

## `def update(self, request, id, body=None, **kwargs)`

* 调用 `self._notifier.info` 直接发送通知程序
* 调用 `self._update`

## `def _update(self, request, id, body, **kwargs)`

1. 调用 `Controller.prepare_request_body` 填充消息体
2. 初始化 policy
3. 调用 `item`，在不进行 policy 检查的情况获取资源情况
4. 将用户需要更新的数据更新到 `item` 获取的数据中
5. 执行权限检查
6. 调用 plugin 的方法
7. 设置 `quotausages` 数据库的 `dirty` 位，提示该更新 quotausages
8. 调用 `self._notifier.info` 发送通知消息。
9. 调用 `registry.notify` 发送系统回调消息。

## `def __getattr__(self, name)`

从 plugin 中获取名为 name 的方法来进行调用。
