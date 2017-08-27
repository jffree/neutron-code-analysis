# Neutron Externel Network Extension

## extension

*neutron/extensions/externel_net.py*

## `class External_net_db_mixin(object)`

*neutron/db/externel_net_db.py*

externel network wsgi 逻辑实现

```
    def __new__(cls, *args, **kwargs):
        new = super(External_net_db_mixin, cls).__new__(cls, *args, **kwargs)
        new._register_external_net_rbac_hooks()
        return new
```

```
    db_base_plugin_v2.NeutronDbPluginV2.register_model_query_hook(
        models_v2.Network,
        "external_net",
        '_network_model_hook',
        '_network_filter_hook',
        '_network_result_filter_hook')
```

```
    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attributes.NETWORKS, ['_extend_network_dict_l3'])
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

注册资源事件的监听










