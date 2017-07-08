# Neutron Ml2 之 ExternalNetwork

我们创建 network 的时候，有一个 `--router:external` 的选项。若在创建 network 的时候指定了该选项，那么就可以从该 network 分配 floating ip。

一份

## extension

*neutron/extensions/externl_net.py*

`class External_net(extensions.ExtensionDescriptor)`

## Model

*neutron/db/external_net_db.py*

`class ExternalNetwork(model_base.BASEV2)`

## `class External_net_db_mixin(object)`

WSGI 实现

* 增加查询过滤选项

```
    db_base_plugin_v2.NeutronDbPluginV2.register_model_query_hook(
        models_v2.Network,
        "external_net",
        '_network_model_hook',
        '_network_filter_hook',
        '_network_result_filter_hook')
```

* 增加构造 network 易读数据时的额外方法

```
    def _extend_network_dict_l3(self, network_res, network_db):
        # Comparing with None for converting uuid into bool
        network_res[external_net.EXTERNAL] = network_db.external is not None
        return network_res

    # Register dict extend functions for networks
    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attributes.NETWORKS, ['_extend_network_dict_l3'])
```

### `def _network_model_hook(self, context, original_model, query)`

为 Network 数据模型增加关联模型 `ExternalNetwork`

```
    def _network_model_hook(self, context, original_model, query):
        query = query.outerjoin(ExternalNetwork,
                                (original_model.id ==
                                 ExternalNetwork.network_id))
        return query
```

### `def _network_filter_hook(self, context, original_model, conditions)`

针对 network 增加 rbac 过滤的钩子方法，也就是验证租户必须有访问该外部网络的权利

### `def _network_result_filter_hook(self, query, filters)`

```
    def _network_result_filter_hook(self, query, filters):
        vals = filters and filters.get(external_net.EXTERNAL, [])
        if not vals:
            return query
        if vals[0]:
            return query.filter((ExternalNetwork.network_id != expr.null()))
        return query.filter((ExternalNetwork.network_id == expr.null()))
```

### `def get_external_network_id(self, context)`

1. 调用 core plugin 的 `get_networks` 方法获取该租户所能访问的所有外部网络
2. 若外部网络的个数大于1，则引发异常
3. 若外部网络的个数等于1，则返回该外部网络的 id

### `def __new__(cls, *args, **kwargs)`

```
    def __new__(cls, *args, **kwargs):
        new = super(External_net_db_mixin, cls).__new__(cls, *args, **kwargs)
        new._register_external_net_rbac_hooks()
        return new
```

### `def _register_external_net_rbac_hooks(self)`

```
    def _register_external_net_rbac_hooks(self):
        registry.subscribe(self._process_ext_policy_create,
                           'rbac-policy', events.BEFORE_CREATE)
        for e in (events.BEFORE_UPDATE, events.BEFORE_DELETE):
            registry.subscribe(self._validate_ext_not_in_use_by_tenant,
                               'rbac-policy', e)
```

注册资源的监听事件，我们下面先来分析这俩方法

### `def _process_ext_policy_create(self, resource, event, trigger, context, object_type, policy, **kwargs)`

1. 验证创建的 rbac 是否是为外部网络创建的
2. 调用 core plugin 的 `get_network` 获取该网络的数据
3. 验证该用户是否有权限访问该网络
4. 调用 `_network_is_external` 验证该网络是否为外部网络
5. 若该网络不是外部网络，则调用 `_process_l3_update` 发送更新外部网络资源的通知，处理数据库的更新问题

### `def _network_is_external(self, context, net_id)`

根据网络的 id，查询 `ExternalNetwork` 数据库来确定该网络是否为外部网络

### `def _process_l3_update(self, context, net_data, req_data, allow_all=True)`

* `allow_all`：若该参数为 True，则意味着该外部网络为 shared，所有用户都可以访问

1. 调用 `registry.notify` 发送更新外部网络的通知
2. 若是将普通网络变更为外部网络，则创建 `ExternalNetwork` 的数据库记录；若 `allow_all` 属性为 True，则创建一个 `NetworkRBAC` 的数据库记录
3. 若是将外部网络变更为普通网络，则首先检查该网络是否在使用，若是在使用，则引发异常；若是未使用，则查询 `ExternalNetwork` 和 `NetworkRBAC` 去除与之有关的数据库记录。
4. 无论如何更新都会更新 `net_data` 的数据

### `def _validate_ext_not_in_use_by_tenant(self, resource, event, trigger, context, object_type, policy, **kwargs)`

* 作用：验证该 rbac 的更新是否会对别的用户造成影响

1. 验证更新或者删除的 rbac 是否是为外部网络创建的
2. 若针对外部网络的更新为发生变动，则不作处理
3. 根据该 rabc 上的 network id 获取该 network id 上的 port，以及与这些 port 所绑定的 router
4. 若是升级该 rabc 前，rbac 的 `target_tenant` 不为 *，则需要判断升级完后，该用户下是否正在有资源依赖于该 network，以及升级后会不会影响继续的使用，若是影响了，则引发异常
5. 若是升级 rbac 前，rbac 的 `target_tenant` 为 *，则需要判断该外网是否为默认外网，若是默认外网则会引发异常，因为默认外网必须是所有用户都可以访问的
6. 若是升级 rbac 前，rbac 的 `target_tenant` 为 *，还需要判断是否有别的租户在使用该 network，若是影响了别的用户的使用，则会引发异常

### `def _process_l3_delete(self, context, network_id)`

在删除外部网络时，需要删除该外部网络所分配出去的所有 floating ip，通过 `l3plugin.delete_disassociated_floatingips` 实现

### `def _process_l3_create(self, context, net_data, req_data)`

在创建外部网络时被调用

1. 调用 `registry.notify` 发送外部网络创建前的通知
2. 增加 `ExternalNetwork` 以及 `NetworkRBAC` 的数据库记录（**外部网络默认是所有用户都可以访问的**）
3. 调用 `registry.notify` 发送外部网络创建后的通知
4. 更新 `net_data` 数据











 