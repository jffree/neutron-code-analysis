# Neutron WSGI 之 rabc policy

* extension : *neutron/extensions/rbac.py*
* WSGI 实现： *neutron/db/rbac_db_mixin.py*
* 数据库模型： *neutron/db/rbac_db_models.py*

目前有两种 rbac 数据库：`NetworkRBAC` 和 `QosPolicyRBAC`


## `class RbacPluginMixin(common_db_mixin.CommonDbMixin)`

### `def get_rbac_policy(self, context, id, fields=None)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/rbac-policies/f45714ee-4e51-452b-b202-ec204c73c087 -H 'Content-Type: application/json' -H 'X-Auth-Token: 939fa920fdf34003b502cd7a8141f109' | jq
```

1. 调用 `_get_rbac_policy` 获取数据库记录
2. 调用 `_make_rbac_policy_dict` 将数据库记录转化为字典形式

### `def _get_rbac_policy(self, context, id)`

1. 调用 `_get_object_type` 根据 id 获取 rbac 类型（`network` 或者 `qos_policy`）
2. 根据类型定位到需要查询的数据库，再根据 id 过滤出想要的记录

### `def delete_rbac_policy(self, context, id)`

1. 调用 `_get_rbac_policy` 获取数据库记录
2. 调用 `registry.notify` 发送通知
3. 执行删除操作

### `def update_rbac_policy(self, context, id, rbac_policy)`

1. 调用 `_get_rbac_policy` 获取数据库记录
2. 调用 `registry.notify` 发送通知
3. 执行更新操作

### `def create_rbac_policy(self, context, rbac_policy)`

1. 调用 `registry.notify` 发送通知
2. 创建数据库记录
3. 返回结果

### `def get_rbac_policies(self, context, filters=None, fields=None,                          sorts=None, limit=None, page_reverse=False)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/rbac-policies -H 'Content-Type: application/json' -H 'X-Auth-Token: 939fa920fdf34003b502cd7a8141f109' | jq
```
直接调用 `_get_collection` 方法获取结果

# 参考

[Neutron RBAC-network 介绍](https://www.ibm.com/developerworks/cn/cloud/library/cl-cn-neutronRBACnetwork/index.html)