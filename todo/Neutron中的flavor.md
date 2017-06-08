# neutron 中的 flavor

1. extension 支持：*neutron/extensions/flavors.py*
2. 数据库类：*neutron/db/flavors_db.py* 中的 `Flavor`、`ServiceProfile`、`FlavorServiceProfileBinding`
3. WSGI 实现类 *neutron/db/flavors_db.py* 中的 `FlavorsDbMixin`

我们重点讲 WSGI 的实现

## `FlavorsDbMixin`

### `def get_flavor(self, context, flavor_id, fields=None)`

测试方法：

```
GET   /v2.0/flavors/{flavor_id}
```

1. 调用 `_get_flavor` 方法查询数据库。
2. 调用 `_make_flavor_dict` 将查询到的数据库转化为字典类型并返回。

### `def _make_flavor_dict(self, flavor_db, fields=None)`

将数据库的查询结果转化为字典类型

### `def create_flavor(self, context, flavor)`

测试方法

```
POST    /v2.0/flavors
```

直接创建一条 `Flavor` 的数据库记录，并返回创建结果

### `def update_flavor(self, context, flavor_id, flavor)`

测试方法

```
PUT   /v2.0/flavors/{flavor_id}
```

1. 调用 `_ensure_flavor_not_in_use` 确保该 flavor 未被使用（该方法未实现）
2. 调用 `_get_flavor` 根据 flavor_id 获取数据库查询记录
3. 更新数据库记录
4. 返回更新后的结果

### `def delete_flavor(self, context, flavor_id)`

测试方法：

```
DELETE    /v2.0/flavors/{flavor_id}
```

1. 调用 `_ensure_flavor_not_in_use` 
2. 调用 `_get_flavor` 根据 flavor_id 获取数据库查询记录
3. 删除数据库记录

### `def get_flavors(self, context, filters=None, fields=None,                    sorts=None, limit=None, marker=None, page_reverse=False)`

测试方法：

```
GET    /v2.0/flavors
```

直接调用 `_get_collection` 来获取数据。

### `def get_service_profile(self, context, sp_id, fields=None)`

测试方法：

```
GET     /v2.0/service_profiles/{profile_id}
```

1. 调用 `_get_service_profile` 根据 `sp_id` 获取数据库（`ServiceProfile`）查询结果
2. 调用 `_make_service_profile_dict` 将数据库查询结果转化为字典形式

### `def create_service_profile(self, context, service_profile)`

测试方法

```
POST   /v2.0/service_profiles
```

1. 调用 `_validate_driver` 验证驱动是否被加载（具体由 `ServiceTypeManager` 来实现）
2. 创建一条 `ServiceProfile` 的数据库记录
3. 返回创建结果

### `def update_service_profile(self, context,                               service_profile_id, service_profile)`

测试方法：

```
PUT   /v2.0/service_profiles/{profile_id}
```

1. 调用 `_validate_driver` 验证驱动
2. 调用 `_ensure_service_profile_not_in_use` 确保该 service_profile 未被使用（在 `FlavorServiceProfileBinding` 数据库中不存在）
3. 调用 `_get_service_profile` 查询到将要修改的数据库记录
4. 更新数据库记录
5. 返回更新后的结果

### `def delete_service_profile(self, context, sp_id)`

1. 调用 `_ensure_service_profile_not_in_use` 确保该 service_profile 未被使用
2. 调用 `_get_service_profile` 获取数据库记录
3. 删除数据库记录

### `get_service_profiles`

```
    def get_service_profiles(self, context, filters=None, fields=None,
                             sorts=None, limit=None, marker=None,
                             page_reverse=False)
```

测试方法：

```
GET  /v2.0/service_profiles
```

直接调用 `_get_collection` 对数据库进行查询


### `get_flavor_next_provider`

```
def get_flavor_next_provider(self, context, flavor_id,
                                 filters=None, fields=None,
                                 sorts=None, limit=None,
                                 marker=None, page_reverse=False)
```

1. 根据 flavor_id 获取 `FlavorServiceProfileBinding` 中的记录
2. 在 `FlavorServiceProfileBinding` 记录中获取 `service_profile_id` 然后调用 `_get_service_profile` 获取 `ServiceProfile` 的数据库记录。
3. 调用 `ServiceTypeManager` 的 `get_service_providers` 方法来获取实现此服务的驱动

### `def get_flavor_service_profile(self, context,                                   service_profile_id, flavor_id, fields=None)`

查询数据库 `FlavorServiceProfileBinding` 内是否存在 `service_profile_id` 和 `flavor_id` 绑定的记录，若存在则返回二者的 `id`

### `def delete_flavor_service_profile(self, context,                                      service_profile_id, flavor_id)`

测试方法：

```
DELETE   /v2.0/flavors/{flavor_id}/service_profiles/{profile_id}
```

查询数据库 `FlavorServiceProfileBinding` 内是否存在 `service_profile_id` 和 `flavor_id` 绑定的记录，若存在则删除此条记录

### `def create_flavor_service_profile(self, context,                                      service_profile, flavor_id)`

测试方法：

```
POST   /v2.0/flavors/{flavor_id}/service_profiles
```
1. 查询 `FlavorServiceProfileBinding` 是否已经存在 `service_profile_id` 和 `flavor_id` 绑定的记录
2. 没有存在的话则创建记录，存在的话则引发异常
3. 返回绑定后的 flavor 信息。

# 参考

其实neutron的 flavor 框架还是依赖于 Service Type 框架的。

[ Neutron/FlavorFramework ](https://wiki.openstack.org/wiki/Neutron/FlavorFramework)

[ Neutron/ServiceTypeFramework ](https://wiki.openstack.org/wiki/Neutron/ServiceTypeFramework)

[ OpenStack网络指南（18）负载均衡服务（LBaaS） ](http://blog.csdn.net/fyggzb/article/details/53924976)