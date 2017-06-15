# Neutron ML2 基类 NeutronDbPluginV2

*neutron/db/db_base_plugin_v2.py*

```
class NeutronDbPluginV2(db_base_plugin_common.DbBasePluginCommon,
                        neutron_plugin_base_v2.NeutronPluginBaseV2,
                        rbac_mixin.RbacPluginMixin,
                        stattr_db.StandardAttrDescriptionMixin)
```

* `DbBasePluginCommon` ml2 的公共方法类
* `NeutronPluginBaseV2` 定义 ml2 plugin 的抽象类
* `RbacPluginMixin` rbac 的 WSGI 实现类
* `StandardAttrDescriptionMixin` **待研究**

这个类实现了 ML2 所需要的大部分公共，其子类 `Ml2Plugin` 也是在此基础上提供其他一些 extension 的功能。

我们先来看 `DbBasePluginCommon` 这个类：

## `class DbBasePluginCommon(common_db_mixin.CommonDbMixin)`

`common_db_mixin.CommonDbMixin` 这个是数据库操作的公共方法类，我介绍过这个模块了。

### `def _generate_mac()`

调用 `utils.get_random_mac` 在 `cfg.CONF.base_mac` 基础上产生 mac 地址

### `def _is_mac_in_use(self, context, network_id, mac_address)`

根据 `network_id` 和 `mac_address` 过滤数据库 `Port`，查看该 mac 地址是否被使用。

### `def _delete_ip_allocation(context, network_id, subnet_id, ip_address)`

根据 `network_id`、`subnet_id`、`ip_address` 删除数据库 `IPAllocation` 中的一条记录。

### `def _store_ip_allocation(context, ip_address, network_id, subnet_id, port_id)`

创建一条 `IPAllocation` 记录

### `def _is_network_shared(self, context, rbac_entries)`

这个方法涉及到 rbac 的认证操作，即若是 context 中的 tenant_id 所指向的客户端有权限访问该 network，则返回True，否则返回 False

### `def _make_subnet_dict(self, subnet, fields=None, context=None)`

将 subnet 的数据库记录转化为字典形式

1. 构造字典
2. 调用 `_is_network_shared` 判断该用户是否有权限访问该 network
3. 调用 `_apply_dict_extend_functions` 查看是否有针对 sudnet 的特殊方法
4. 调用 `_fields` 进行最后的过滤操作。

### `def _make_subnetpool_dict(self, subnetpool, fields=None)`

将 subnetpool 的数据库记录转化为字典形式

### `def _make_port_dict(self, port, fields=None, process_extensions=True)`

将 Port 的一条记录转化为字典形式

### `def _get_network(self, context, id)`

调用公共方法里面的 `_get_by_id` 查询 `models_v2.Network` 数据库

### `def _get_subnet(self, context, id)`

调用公共方法里面的 `_get_by_id` 查询 `models_v2.Subnet` 数据库

### `def _get_subnetpool(self, context, id)`

以 objects 的方式获取数据库 `subnetpools` 一条记录

### `def _get_port(self, context, id)`

调用公共方法里面的 `_get_by_id` 查询 `models_v2.Port` 数据库

### `def _get_dns_by_subnet(self, context, subnet_id)`

以 objects 的方式从 `DNSNameServer` 数据库中获取一条记录

### `def _get_route_by_subnet(self, context, subnet_id)`

从 `SubnetRoute` 获取所有与 `subnet_id` 相关的记录

### `def _get_router_gw_ports_by_network(self, context, network_id)`

获取该 network_id 所指向网络中的用于路由网关的 port

### `def _get_subnets_by_network(self, context, network_id)`

获取数据 network_id 所指向网络的所有子网

### `def _get_subnets_by_subnetpool(self, context, subnetpool_id)`

获取属于 `subnetpool_id` 所指向的子网池的所有子网

### `def _get_all_subnets(self, context)`

查询数据库 `subnets` 获取所有子网

### `def _get_subnets(self, context, filters=None, fields=None,                     sorts=None, limit=None, marker=None,                     page_reverse=False)`

根据过滤条件获取子网，并可进行排序、分页的操作

### `def _make_network_dict(self, network, fields=None,                           process_extensions=True, context=None)`

将 network 的数据库转化为字典格式

### `def _make_subnet_args(self, detail, subnet, subnetpool_id)`

填充针对子网请求的参数

### `def _make_fixed_ip_dict(self, ips)`

将 IP 的记录转化为字典

### `def _port_filter_hook(self, context, original_model, conditions)`

对于非管理员用户，若想访问 port 资源需要拥有这个 port 所属的 network 的权限

### `def _port_query_hook(self, context, original_model, query)`

调用 sqlalchemy 的 `outerjoin` 方法，与 `Network` 模型进行联合查询

## 类属性

```
    __native_bulk_support = True
    __native_pagination_support = True
    __native_sorting_support = True
```

这表明支持批量、分页、排序操作。

## `def __init__(self)`

1. 定义 ipam 后端（关于ipam，请参考我写的 **Neutron 之 IPAM**）
2. 若在配置文件中设置了 `notify_nova_on_port_status_changes`，则会监听几个数据库事件：
 1. models_v2.Port, 'after_insert', self.nova_notifier.send_port_status
 2. models_v2.Port, 'after_update', self.nova_notifier.send_port_status
 3. models_v2.Port.status, 'set', self.nova_notifier.record_port_status_changed
3. 订阅 rabc 事件
 1. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_CREATE
 2. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_UPDATE
 3. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_DELETE




























