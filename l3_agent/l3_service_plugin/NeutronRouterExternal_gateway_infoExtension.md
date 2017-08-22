# Neutron Router external_gateway_info extension

* extension : *neutron/extensions/l3_ext_gw_mode.py*

## `class L3_NAT_dbonly_mixin(l3_db.L3_NAT_dbonly_mixin)`

对 router external_gateway_info extension 逻辑业务的实现。

*neutron/db/l3_gwmode_db.py*

*子类和父类的名称是一样的，但是在不同的模块*

```
    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        l3.ROUTERS, ['_extend_router_dict_gw_mode'])

    def _extend_router_dict_gw_mode(self, router_res, router_db):
        if router_db.gw_port_id:
            nw_id = router_db.gw_port['network_id']
            router_res[EXTERNAL_GW_INFO] = {
                'network_id': nw_id,
                'enable_snat': router_db.enable_snat,
                'external_fixed_ips': [
                    {'subnet_id': ip["subnet_id"],
                     'ip_address': ip["ip_address"]}
                    for ip in router_db.gw_port['fixed_ips']
                ]
            }
```

扩展 router 的显示属性

### `def _update_router_gw_info(self, context, router_id, info, router=None)`

1. 若 router 为空则调用 `_get_router` 获取其数据库记录
2. 调用 `_get_enable_snat` 获取该 router 是否支持 snat
3. 调用 `L3_NAT_dbonly_mixin._update_router_gw_info` 方法实现具体的业务逻辑

### `def _get_enable_snat(info)`

1. 若 info 数据中包含 `enable_snat` 属性，则使用 info 中的数据
2. 若不包含，则使用默认的 `cfg.CONF.enable_snat_by_default`

### `def _build_routers_list(self, context, routers, gw_ports)` 

```
    def _build_routers_list(self, context, routers, gw_ports):
        for rtr in routers:
            gw_port_id = rtr['gw_port_id']
            # Collect gw ports only if available
            if gw_port_id and gw_ports.get(gw_port_id):
                rtr['gw_port'] = gw_ports[gw_port_id]
                # Add enable_snat key
                rtr['enable_snat'] = rtr[EXTERNAL_GW_INFO]['enable_snat']
        return routers
```