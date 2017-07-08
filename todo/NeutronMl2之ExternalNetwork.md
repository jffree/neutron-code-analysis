# Neutron Ml2 之 ExternalNetwork

我们创建 network 的时候，有一个 `--router:external` 的选项。若在创建 network 的时候指定了该选项，那么就可以从该 network 分配 floating ip。

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




