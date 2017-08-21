# Neutron Router Route extension

* extension : *neutron/extensions/extraroute.py*

## `class ExtraRoute_dbonly_mixin(l3_db.L3_NAT_dbonly_mixin)`

对 router route （`Extraroute` extension）逻辑业务的实现。

*neutron/db/extraroute_db.py*

```
    def _extend_router_dict_extraroute(self, router_res, router_db):
        router_res['routes'] = (ExtraRoute_dbonly_mixin.
                                _make_extra_route_list(
                                    router_db['route_list']
                                ))

    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        l3.ROUTERS, ['_extend_router_dict_extraroute'])
```

```
    def _make_extra_route_list(extra_routes):
        return [{'destination': route['destination'],
                 'nexthop': route['nexthop']}
                for route in extra_routes]
```

扩展 router 的属性，将 route 添加进去

### `def update_router(self, context, id, router)`

1. 若是待更新的 router 数据中包含 `routes` 属性，则调用 `_update_extra_routes` 更新 `RouterRoute` 数据库的记录
2. 调用 `_get_extra_routes_by_router_id` 获取当前 router 应有的 route 记录
3. 调用 `ExtraRoute_dbonly_mixin.update_router` 执行更新 router 的业务操作
4. 返回更新后的 router 数据

### `def _update_extra_routes(self, context, router, routes)`

1. 调用 `_validate_routes` 验证 routes 数据是否合法
2. 调用 `_get_extra_routes_dict_by_router_id` 获取已有的 route 记录
3. 找出删除的以及增加的 route 表项
4. 在数据库 `RouterRoute` 创建新增的 route 表项，删除那些被删除的表项

### `def _validate_routes(self, context, router_id, routes)`

1. routes 记录的数量不能超过设定值（`cfg.CONF.max_routes`）
2. 通过 ml2 获取与该 router 绑定的所有 port 的 ip 及其子网的 cidr
3. 调用 `_validate_routes_nexthop` 验证 nexthop 是否合法

### `def _validate_routes_nexthop(self, cidrs, ips, routes, nexthop)`

1. 验证 nexthop 必须是可达的
2. 验证 nexthop 没有在当前的 router 上使用

### `def _get_extra_routes_dict_by_router_id(self, context, id)`

获取当前 router 上关于 route 的记录

### `def _get_subnets_by_cidr(self, context, cidr)`

获取与 cidr 相符的 subnet 记录

### `def _get_extra_routes_by_router_id(self, context, id)`

与 `_get_extra_routes_dict_by_router_id` 类似，都是获取当前 router 所拥有的 route

### `def _confirm_router_interface_not_in_use(self, context, router_id, subnet_id)`

1. 调用 `L3_NAT_dbonly_mixin._confirm_router_interface_not_in_use` 确认该 router 是否还被使用
2. 验证该 router 上的 route 是否对与 subnet 来说还在被需要。（若被需要则会引发异常，表示不能被删除）