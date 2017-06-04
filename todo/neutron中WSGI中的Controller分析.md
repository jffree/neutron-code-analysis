# Neutron 中 WSGI Controller 分析

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

## `def _view(self, context, data, fields_to_strip=None)`

调用 `_exclude_attributes_by_policy` 与 `_filter_attributes` 返回用户可见的属性。

## `def index(self, request, **kwargs)`

* 初始化 policy
* 调用 `_items` 方法

## `def _items(self, request, do_authz=False, parent_id=None)`

