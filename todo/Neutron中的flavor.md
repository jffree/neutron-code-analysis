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












