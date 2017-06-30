# Neutron ipam 之 IpamPluggableBackend

*neutron/db/ipam_pluggable_backend.py*

```
class IpamBackendMixin(db_base_plugin_common.DbBasePluginCommon)
class IpamPluggableBackend(ipam_backend_mixin.IpamBackendMixin)
```

我们就从 `IpamBackendMixin` 看起

## 测试命令：

* 创建网络

```
neutron net-create --shared simple-network
```

* 创建子网

```
neutron subnet-create --name simple-subnet --allocation-pool start=10.10.12.200,end=10.10.12.210 --allocation-pool start=10.10.12.220,end=10.10.12.230 simple-network 10.10.12.0/24
```

## 参考（特别重要）

[netaddr](https://netaddr.readthedocs.io/en/latest/index.html)

## `class IpamBackendMixin(db_base_plugin_common.DbBasePluginCommon)`

### `def validate_pools_with_subnetpool(self, subnet)`

在创建子网时，可能会指定从 subnet_pool 中分配子网的 ip，这时会调用该方法验证请求是否合法。

1. 调用 `validators.is_attr_set` 判断 subnet 属性中是否包含 `allocation_pools` 和 `cidr`。
2. 若 subnet 属性中包含 `allocation_pools` 时，则必须包含 `cidr` 属性。

### `def generate_pools(self, cidr, gateway_ip)`

在创建子网时，根据 `cidr` 和 `gateway_ip` 生成 `allocation_pools`，调用 `ipam_utils.generate_pools` 实现

### `def pools_to_ip_range(ip_pools)`

将地址池用 `IPRange` 来描述。

默认状态下的地址池描述为：

```
{"start": "10.10.12.200", "end": "10.10.12.210"} 
{"start": "10.10.12.220", "end": "10.10.12.230"}
```

### `def validate_allocation_pools(self, ip_pools, subnet_cidr)`

对子网的地址池（`allocation pools`）进行验证

* `ip_pools`：以 `IpRange` 描述的 ip 地址池
* `subent_cidr`：以 cidr 描述的 ip 地址范围

1. 检查 ip_pools 内的 ip 地址版本是否同 cidr 描述的一致
2. 检查 ip_pools 内的 ip 地址范围是否超出了 cidr 涵盖的范围
3. 检查 ip_pools 所包含的所有地址池，看地址池内的地址是否有重复的出现

### `def validate_gw_out_of_pools(self, gateway_ip, pools)`

网关地址是不能在地址池内的。该方法就是验证这个问题。

### `def update_db_subnet(self, context, subnet_id, s, oldpools)`

1. 若更新数据中包含 `dns_nameservers` 属性，则调用 `_update_subnet_dns_nameservers` 更新 dns nameserver 的数据库记录
2. 若更新数据中包含 `host_routes` 属性，则调用 `_update_subnet_host_routes` 更新 host routes 的数据库记录

### `def _update_subnet_dns_nameservers(self, context, id, s)`

* 测试方法：

```
neutron subnet-update b4634777-a30d-4001-a0c0-256530a01619 --dns-nameserver 114.114.114.114 --dns-nameserver 8.8.8.8
```

* 数据库结果

```
MariaDB [neutron]> select * from dnsnameservers;
+-----------------+--------------------------------------+-------+
| address         | subnet_id                            | order |
+-----------------+--------------------------------------+-------+
| 114.114.114.114 | b4634777-a30d-4001-a0c0-256530a01619 |     0 |
| 8.8.8.8         | b4634777-a30d-4001-a0c0-256530a01619 |     1 |
+-----------------+--------------------------------------+-------+
```

1. 调用 `DbBasePluginCommon._get_dns_by_subnet` 获取该子网在更新前对应的 dns namserver 的 object（**注意：**一个 subnet 可能包含多个 dns nameserver）。
2. 删除旧的 dns nameserver 数据库记录
3. 创建新的 dns nameserver 的数据库记录
 
### `def _update_subnet_host_routes(self, context, id, s)`





## `class IpamPluggableBackend(ipam_backend_mixin.IpamBackendMixin)`

### `def update_db_subnet(self, context, id, s, old_pools)`

* 参数介绍
 * `context`：
 * `id`：待更新的子网 id
 * `s`：子网的新属性
 * `old_pools`：子网之前的地址池

1. 调用父类的 `update_db_subnet`










