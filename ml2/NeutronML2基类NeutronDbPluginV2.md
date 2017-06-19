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

## `NeutronDbPluginV2`

### 类属性

```
    __native_bulk_support = True
    __native_pagination_support = True
    __native_sorting_support = True
```

这表明支持批量、分页、排序操作。

### `def __init__(self)`

1. 定义 ipam 后端（关于ipam，请参考我写的 **Neutron 之 IPAM**）
2. 若在配置文件中设置了 `notify_nova_on_port_status_changes`，则会监听几个数据库事件：
 1. models_v2.Port, 'after_insert', self.nova_notifier.send_port_status
 2. models_v2.Port, 'after_update', self.nova_notifier.send_port_status
 3. models_v2.Port.status, 'set', self.nova_notifier.record_port_status_changed
3. 订阅 rabc 事件
 1. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_CREATE
 2. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_UPDATE
 3. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_DELETE


### `def validate_network_rbac_policy_change(self, resource, event, trigger, context, object_type, policy, **kwargs)`

回调函数，用于接收 rbac_policy 资源的变化。

1. 只关心在 network 资源上的 access_as_shared 动作
2. 对于资源的创建和删除来说，用户必须有对应的权限
3. 对于资源的创建和删除来说，若是改变了可访问资源的 tenant，则需要调用 `ensure_no_tenant_ports_on_network` 来检查是否还有改租户的 port 资源绑定在这个网络资源上。

### `def ensure_no_tenant_ports_on_network(self, network_id, net_tenant_id, tenant_id)`

1. 根据 `network_id` 查询 `NetworkRBAC` 数据库
2. 根据 `network_id` 查询 `Port` 数据库
3. 查询该 `tenant_id` 租户下否有 `port` 资源绑定在这个 `network` 上，有的话则引发异常。

### `def get_network(self, context, id, fields=None)`

从这里开始，我们开始接触核心资源的 WSGI 接口

1. 调用 `DbBasePluginCommon._get_network` 获取数据库记录
2. 调用 `_make_network_dict` 将数据库记录转化为字典形式

### `def get_networks(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

1. 构造 Maker
2. 调用 `_get_collection` 进行数据库查询，并返回字典格式

### `def get_networks_count(self, context, filters=None)`

调用 `_get_collection_count` 返回过滤后的网络资源数量

### `def delete_network(self, context, id)`

1. 调用 `_get_network` 获取数据库记录
2. 查询该 network 上是否有再使用的 port（非 dhcp），若是有的话则引发异常
3. 调用 `_get_subnets_by_network` 获取与该网络绑定的子网
4. 循环调用 `delete_subnet` 删除该网络下的所有子网 

### `def update_network(self, context, id, network)`

1. 调用 `_get_network` 获取网络信息
2. 当要更新 network 的 shared 属性时，需要对该 network 的 rbac 规则进行检查
 1. 调用 `_validate_shared_update` 验证 share 属性是否可以被更新
 2. 根据 shared 的设定进行 rbac 的规则更新
3. 调用 `_filter_non_model_columns` 过滤掉  `network` 数据中非数据库的那部分
4. 更新数据库

### `def create_network(self, context, network)`

1. 调用 `create_network_db` 
2. 调用 `_make_network_dict` 返回字典类型的创建结果

### `def create_network_db(self, context, network)`

1. 创建一个 `Network` 的数据库记录
2. 若是该 network 的 shared 为 True，则创建一条 `NetworkRBAC` 数据库记录

从这里我们看出：**网络资源只是一个概念，真正的有效的是子网和端口**

### `def create_network_bulk(self, context, networks)`

批量创建网络，直接调用 `_create_bulk` 方法

### `def _create_bulk(self, resource, context, request_items)`

这个方法比较简单，就是对 `'create_%s' % resource` 的循环调用

### `def get_subnet(self, context, id, fields=None)`

1. 调用 `_get_subnet` 获取数据库记录
2. 调用 `_make_subnet_dict` 将数据库记录转化为字典形式

### `def get_subnets(self, context, filters=None, fields=None,                    sorts=None, limit=None, marker=None, page_reverse=False)`

直接调用 `_get_subnets` 

### `def _get_subnets(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

根据过滤条件、分页、排序的要求调用 `_get_collection` 

### `def get_subnets_count(self, context, filters=None)`

根据过滤条件，调用 `_get_collection_count`，获取子网数量












### `def _validate_shared_update(self, context, id, original, updated)`

验证是否可以更新 network 资源的 shared 属性

当想要更新 shared 为 false 时，若有多个租户在使用这个 network 资源，则不可以更新，引发异常。

### `def delete_subnet(self, context, id)`

1. 调用 `_get_subnet` 获取数据库记录
2. 调用 `_check_subnet_not_used` 判断该子网是否被使用
3. 将 `IPAllocation` 与 `Port` 进行联合查询，找到与该子网绑定的端口
4. 调用 `ipv6_utils.is_auto_address_subnet` 方法，判断该子网是否是 ipv6 且自动生成 ipv6 地址的类型
5. 若该子网是自动生成 ipv6 地址的类型，则调用 `_subnet_check_ip_allocations_internal_router_ports` 判断是否该子网是否拥有路由器用于分配 ip 的端口，若是有的话则不能删除
6. 若该子网不是自动生成 ipv6 地址的类型，则过滤出可以自动删除的与该子网绑定的端口
7. 删除所有可自动删除的端口
8. 调用 `_subnet_check_ip_allocations` 查询是否还有分配了 ip 的 port 与该子网绑定，若有的话则引发异常，不能删除子网
9. 没有其余的绑定后，删除子网的数据库记录
10. 调用 ipam 的 `delete_subnet`

### `def _subnet_check_ip_allocations(self, context, subnet_id)`

查询该子网上是否有 port 绑定（分配了 ip）

### `def _subnet_get_user_allocation(self, context, subnet_id)`

检查是否有非 `AUTO_DELETE_PORT_OWNERS` 类型的 port 与该子网绑定

### `def update_subnet(self, context, id, subnet)`

1. 调用 `_get_subnet` 获取数据库记录
2. 调用 `_validate_subnet` 验证数据
3. 对于 ipv6 来说，若 `subnetpool_id` 为 `const.IPV6_PD_POOL_ID`，则自动生成 `gateway_ip` 和 `allocation_pools` 对应的数据
4. 若数据中包含 `allocation_pools` 的数据，则调用 `ipam` 的 `pools_to_ip_range` 和 `validate_allocation_pools` 来验证数据。
5. 当 `gateway_ip` 发生被更新时，需要调用 `ipam.validate_gw_out_of_pools` 来进行验证 gateway 是否在 pools 中。调用 `registry.notify` 发送 gateway 变更的通知（貌似还没有客户订阅这个消息）
6. 调用 `ipam.update_db_subnet` 更新数据库
7. 调用 `_make_subnet_dict` 生成子网的字典类型的数据
8. 对于 ipv6 来说可能会自动更新一些与该子网绑定的 port 
9. 更新 port 的同时可能会更新路由器信息
10. 调用 `registry.notify` 发送网关更新完毕的消息

### `def _validate_subnet(self, context, s, cur_subnet=None)`

验证新的子网数据 s 与旧子网数据 cur_subnet 是否有冲突。当 cur_subnet 为空时，验证 s 是否合法。

1. 调用 `_validate_ip_version` 验证 ip 版本的设定是否合法
2. 检查 cidr 是否符合要求：
 1. 网络前缀是否符合要求
 2. 是否为多播地址
 3. 是否为本地回环地址
3. 检查子网网关设置是否合法
 1. 调用 `_validate_ip_version` 检查网关的ip类型是否合法
 2. 调用 ipam 的 `check_gateway_invalid_in_subnet` 方法，验证网关地址对于子网地址来说是否合法（在子网地址内且不为网络地址和广播地址）
 3. 验证该 gateway 没有被分配到 port 端口上
4. 若是子网数据 s 中包含了 `dns_nameservers`，则验证此数据是否合法
5. 若是子网数据 s 中包含了 `host_routes`，则调用 `_validate_host_route` 验证此数据是否合法
6. 如果为 ipv4 版本，则不可以设置 `ipv6_ra_mode` 和 `ipv6_address_mode`
7. 若果为 ipv6Ban本，则调用 `_validate_ipv6_attributes` 来验证数据是否符合规定

### `def _validate_host_route(self, route, ip_version)`

验证路由记录是否合法。

路由记录是个列表，列表里面是一系列的字典：
```
[
  {'destination':data,
   'nexthop':data
  },
  {
   ...
  },
]
```

1. 验证是否为合法的网络地址和ip 地址
2. 验证 ip 的版本是否符合要求

### `def _validate_ipv6_update_dhcp(self, subnet, cur_subnet)`

对于 ipv6 版本，来说若是更新子网的 `enable_dhcp` 为 False，则不允许设定 `ipv6_ra_mode` 和 `ipv6_address_mode` 两个选项。

### `def _validate_ipv6_attributes(self, subnet, cur_subnet)`

验证 ipv6 版本的子网数据。 subnet 代表新的（将要更新的）数据，cur_subnet 代表当前数据。

1. 最是更新数据（即 cur_subnet 不为空），则调用 `_validate_ipv6_update_dhcp` 检查 dhcp 的更新是否合法
2. 若不是更新那么就是创建，则调用 `_validate_ipv6_dhcp` 验证 subnet 的dhcp 数据是否合法
3. 若是 `ipv6_ra_mode` 和 `ipv6_address_mode` 被同时设定，则这两个属性的数据必须系统，这里会调用 `_validate_ipv6_combination` 来验证
4. 调用 `_validate_eui64_applicable` 验证 ipv6 的 cidr 的网络前缀是否合法，openstack 中要求必须为 64位


### `def create_subnet(self, context, subnet)`

1. `cidr` 和 `prefixlen` 不可同时提供
2. 提供了 cidr 时，构造 cidr
3. 调用 `_get_subnetpool_id` 查看用户是否声明了使用那个 subnetpool 
4. 如果确认了 subnetpool_id 则调用 `ipam.validate_pools_with_subnetpool` 进行检查工作。同时，若是 ipv6，则进行 ipv6 的一些检查（`_validate_subnet`）
5. 没有 subnetpool_id 则执行 `_validate_subnet` 进行检查
6. 调用 `_create_subnet`

### `def _get_subnetpool_id(self, context, subnet)`

从创建 subnet 的请求中提取 `subnetpool_id`。（默认的或者用户提供的）

若使用默认的 subnetpool 则会调用 `get_default_subnetpool` 方法

`get_default_subnetpool` 方法会调用 `get_subnetpools` 来获取默认的 subnetpool

### `def _create_subnet(self, context, subnet, subnetpool_id)`

1. 调用 `_get_network` 来获取子网绑定的网络
2. 调用 `ipam.allocate_subnet` 生成子网
3. 若该子网绑定的网络的 externel 属性为 True，则调用 `_update_router_gw_ports` 更新路由信息
4. 若该子网为 ipv6 且自动分配地址则调用 `ipam.add_auto_addrs_on_network_ports` 获取需要更新的 port，同时更新 port
5. 调用 `_make_subnet_dict` 返回创建成功的 subnet 信息。

### `def _update_router_gw_ports(self, context, network, subnet)`

这个方法要达到这么一个目的：当外部网关接口上只绑定了一定类型（ipv4/ipv6）的网络地址时，若有新的类型的子网地址加入的话，会自动在这个端口上绑定一个新类型的子网地址。

1. 获取 L3 的 service plugin
2. 获取与该网络绑定的网关接口
3. 获取这些端口所有的 router id
4. 查看网关地址是否为两个不同的种类，若不是的话，则增加新的这个子网种类。

**注意：**当你在 horizon 上操作来尝试这个功能时，一定要在 admin 面板下的 network 下添加子网，这样在才会生效。在 project 下的 network 下添加是不会生效的。

### `def create_subnet_bulk(self, context, subnets)`

批量创建子网：直接调用 `_create_bulk` 方法实现。

### `def get_subnetpool(self, context, id, fields=None)`

调用 `_get_subnetpool` 获取数据库记录
调用 `_make_subnetpool_dict` 构造消息体

### `def get_subnetpools(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

调用 `subnetpool_obj.SubnetPool.get_objects` 获取数据库记录
调用 `_make_subnetpool_dict` 构造消息体

### `def delete_subnetpool(self, context, id)`

1. 调用 `_get_subnetpool` 获取数据库记录
2. 调用 `_get_subnets_by_subnetpool` 判断有没有分配出去的子网
3. 删除数据库

### `def update_subnetpool(self, context, id, subnetpool)`

1. 调用 `_get_subnetpool` 获取之前的数据库记录
2. 调用 `_update_subnetpool_dict` 构造升级数据
3. 若将此 subnetpool 升级为 default 子网池，则会调用 `_check_default_subnetpool_exists` 检查是否已经存在默认的子网池。
4. 若旧数据有 `address_scope_id`，则会调用 `_check_subnetpool_update_allowed` 检查该地址范围是否符合要求
5. 调用 `_validate_address_scope_id` 方法验证地址范围是否合法
6. 升级数据库记录
7. 若是地址范围发生了变化，则调用 `registry.notify` 发送通知，这个还真有方法在监听 `_notify_subnetpool_address_scope_update`
8. 调用 `_apply_dict_extend_functions` 施加附加方法构造返回的结构体

### `def _validate_address_scope_id(self, context, address_scope_id,                                   subnetpool_id, sp_prefixes, ip_version)`

1. 检查 `is_address_scope_owned_by_tenant` 地址范围
2. 调用 `get_ip_version_for_address_scope` 获取地址范围的 ip 版本，检查 subnetpool 的 ip 版本是否符合地址范围的版本
3. 根据 `address_scope_id` 获取所有与之绑定的子网池，判断子网池内的地址是否出现了重叠，重叠则引发异常

### `def create_subnetpool(self, context, subnetpool)`

1. 若该子网池被设定为默认的，则调用 `_check_default_subnetpool_exists` 检查是否有默认的子网池存在
2. 调用 `_validate_address_scope_id` 验证数据
3. 创建数据库记录
4. 返回创建结果









## 其他方法

### `def _check_subnet_not_used(context, subnet_id)`

调用 `registry.notify` 发送调用订阅程序

```
registry.notify(
            resources.SUBNET, events.BEFORE_DELETE, None, **kwargs)
```

没有找到订阅 subnet before_delete 的回调

### `def get_first_host_ip(net, ip_version)`

获取 net 中的第一个可用的 ip 地址

### `def _update_subnetpool_dict(orig_pool, new_pool)`

将新的 subnetpool 数据与旧的数据对比，构造出将要升级的数据
这里面会检查 prefix，要求更新的 prefix 的范文要比旧的大


# 参考

[ Mysql left join，right join，inner join，outer join之图解 ](http://narutolby.iteye.com/blog/1893506)
[netaddr 0.7.19 documentation](https://netaddr.readthedocs.io/en/latest/#netaddr-0-7-19-documentation)










