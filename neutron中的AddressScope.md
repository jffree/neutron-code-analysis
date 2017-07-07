# Neutron 之 AddressScope

`AddressScope` 其实就是用来限定某个 subnetpool 的 ip 版本

## 测试

```
neutron address-scope-create --shared test 4
Created a new address_scope:
+------------+--------------------------------------+
| Field      | Value                                |
+------------+--------------------------------------+
| id         | 6ed242e0-13c9-4dfb-a455-bf63436d47c0 |
| ip_version | 4                                    |
| name       | test                                 |
| project_id | d4edcc21aaca452dbc79e7a6056e53bb     |
| shared     | True                                 |
| tenant_id  | d4edcc21aaca452dbc79e7a6056e53bb     |
+------------+--------------------------------------+
```


## extensions

*neutron/extensions/address_scope.py*

`class Address_scope(extensions.ExtensionDescriptor)`

`class AddressScopePluginBase(object)`

## Model

*neutron/db/models/address_scope.py*

`class AddressScope(model_base.BASEV2, model_base.HasId, model_base.HasProject)`

## WSGI 实现

*neutron/db/address_scope_db.py*

## `class AddressScopeDbMixin(ext_address_scope.AddressScopePluginBase)`

```
    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attr.NETWORKS, ['_extend_network_dict_address_scope'])
```

### `def _extend_network_dict_address_scope(self, network_res, network_db)`

扩展 `network` 的返回属性，将 `ipv4_address_scope` 和 `ipv6_address_scope` 加入到其中

### `def is_address_scope_owned_by_tenant(self, context, id)`

检测当前访问的租户是否有权限访问该 address_scope

### `def get_address_scope(self, context, id, fields=None)`

1. 调用 `_get_address_scope` 获取 `AddressScope` 数据库的记录
2. 调用 `_make_address_scope_dict` 将 `AddressScope` 数据库记录转化为易读的形式

### `def _get_address_scope(self, context, id)`

根据 ID 读取 `_make_address_scope_dict` 数据库记录

### `def _make_address_scope_dict(self, address_scope, fields=None)`

将 `AddressScope` 数据库记录转化为易读的形式

### `def get_address_scopes(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

调用 `_get_collection` 进行 `AddressScope` 数据库的批量查询。

### `def get_address_scopes_count(self, context, filters=None)`

获取满足过滤条件 filter 的数据库记录的数量

### `def delete_address_scope(self, context, id)`

1. 通过调用 `AddressScope` object 判断该 id 的数据库是否在被使用
2. 若未被使用则删除数据库记录，被使用则引发异常

### `def update_address_scope(self, context, id, address_scope)`

更新 `AddressScope` 的数据库记录（不可将 `shared` 改变为非 `shared`）

### `def create_address_scope(self, context, address_scope)`

增加一条 `AddressScope` 的数据库记录

### `def get_ip_version_for_address_scope(self, context, id)`

获取一个 `AddressScope` 数据库记录的 ip 版本