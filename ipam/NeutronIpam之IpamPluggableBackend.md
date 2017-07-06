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
3. 若更新数据中包含 `allocation_pools` 属性，则调用 `_update_subnet_allocation_pools` 更新 allocation pools 的数据库记录
4. 若更新数据中包含 `service_types` 属性，则调用 `_update_subnet_service_types` 更新 service type 的数据库记录
5. 调用 `_get_subnet` 获取原 subnet 的数据库记录，更新数据库记录
6. 返回更新后的 subnet 数据库记录，返回更新的与 subnet 数据有关的其他数据库记录

从这里可以看出，与 subnet 有关的数据库分别为：`DNSNameServer`、`SubnetRoute`、`IPAllocationPool`、`SubnetServiceType`

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
4. 删除更新数据中的 `dns_nameservers` 属性（因为已经更新），返回更新的结果
 
### `def _update_subnet_host_routes(self, context, id, s)`

* 测试方法：

```
neutron subnet-update b4634777-a30d-4001-a0c0-256530a01619 --host-route destination=172.16.100.0/24,nexthop=10.10.12.1 --host-route destination=192.168.40.0/24,nextho
p=10.10.12.2
```

* 数据库记录

```
MariaDB [neutron]> select * from subnetroutes;
+-----------------+------------+--------------------------------------+
| destination     | nexthop    | subnet_id                            |
+-----------------+------------+--------------------------------------+
| 172.16.100.0/24 | 10.10.12.1 | b4634777-a30d-4001-a0c0-256530a01619 |
| 192.168.40.0/24 | 10.10.12.2 | b4634777-a30d-4001-a0c0-256530a01619 |
+-----------------+------------+--------------------------------------+
```

1. 调用 `DbBasePluginCommon._get_route_by_subnet` 根据子网的 id，获取该子网下的路由（数据库 `SubnetRoute`）记录
2. 删除无效的数据库记录，增加新增的数据库记录
3. 删除更新数据中的 `host_routes` 属性（因为已经更新），返回更新的结果

### `def _update_subnet_allocation_pools(self, context, subnet_id, s)`

* 更新前的 `IPAllocationPool` 记录：

```
MariaDB [neutron]> select * from ipallocationpools where subnet_id='b4634777-a30d-4001-a0c0-256530a01619';
+--------------------------------------+--------------------------------------+--------------+--------------+
| id                                   | subnet_id                            | first_ip     | last_ip      |
+--------------------------------------+--------------------------------------+--------------+--------------+
| 1665256b-5f5f-4230-b9d2-96cd24d9837b | b4634777-a30d-4001-a0c0-256530a01619 | 10.10.12.220 | 10.10.12.230 |
| b9710743-50e6-4828-8854-87d2065266f1 | b4634777-a30d-4001-a0c0-256530a01619 | 10.10.12.200 | 10.10.12.210 |
+--------------------------------------+--------------------------------------+--------------+--------------+
```

* 更新 subnet：

```
neutron subnet-update b4634777-a30d-4001-a0c0-256530a01619 --allocation-pool start=10.10.12.100,end=10.10.12.110 --allocation-pool start=10.10.12.120,end=10.10.12.130 
```

* 更新后的 `IPAllocationPool` 记录

```
MariaDB [neutron]> select * from ipallocationpools where subnet_id='b4634777-a30d-4001-a0c0-256530a01619';
+--------------------------------------+--------------------------------------+--------------+--------------+
| id                                   | subnet_id                            | first_ip     | last_ip      |
+--------------------------------------+--------------------------------------+--------------+--------------+
| 80a3f992-0fc1-400a-8c6e-0068485518cd | b4634777-a30d-4001-a0c0-256530a01619 | 10.10.12.100 | 10.10.12.110 |
| 89f3405c-be87-40ac-8aa6-33e6c5f24d4c | b4634777-a30d-4001-a0c0-256530a01619 | 10.10.12.120 | 10.10.12.130 |
+--------------------------------------+--------------------------------------+--------------+--------------+
```

1. 根据子网的 id 删除该子网下的原 allocation pools 数据库 `IPAllocationPool` 的记录
2. 根据更新的子网资源的数据 s，增加新的数据库 `IPAllocationPool` 的记录
3. 删除更新数据中的 `allocation_pools` 属性（因为已经更新），返回增加的数据库的结果

### `def _update_subnet_service_types(self, context, subnet_id, s)`

**关于 subnet 的 `service_types` 属性的解释：**

*`service_types`，定义该 subnet 的用途，为手动指定的 device_owner 的列表。如：`network:floatingip_agent_gateway`、`network:router_gateway`。port 分配 IP 时, 通过 port 的 `device_owner` 匹配 subnet 的 `service_type`，来决定在哪个 subnet 中分配 IP。*

[Neutron社区每周记（10.24-10.28）| Neutron 终于不“浪费”公网 IP 了](http://www.wxzhi.com/archives/576/5pncjemqwbsgav7f/)

1. 根据子网的 id 删除该子网下的数据库 `SubnetServiceType` 的记录
2. 根据更新的子网资源的数据 s，增加新的数据库 `SubnetServiceType` 的记录
3. 删除更新数据中的 `service_types` 属性（因为已经更新），返回增加的数据库的结果

### `def _validate_ip_version_with_subnetpool(self, subnet, subnetpool)`

验证子网数据中的 ip 版本与子网池的 ip 版本一致

### `def _gateway_ip_str(subnet, cidr_net)`

获取子网数据的网关地址，若子网数据中不包含网关地址，则将网络地址之上的第一个地址作为网关地址

### `def _prepare_allocation_pools(self, allocation_pools, cidr, gateway_ip)`

1. 若 `allocation_pools` 没有设置，则调用 `generate_pools` 方法生成地址池并返回。
2. 若 `allocation_pools` 被设置，则调用 `pools_to_ip_range` 用 `netaddr.IPRange` 来描述地址池
3. 调用 `validate_allocation_pools` 验证地址池相对于 `cidr` 来说是否合法
4. 调用 `validate_gw_out_of_pools` 验证网关地址不在地址池内
5. 返回以 `IPRange` 描述的地址池

### `def _make_subnet_args(self, detail, subnet, subnetpool_id)`

将创建 subnet 的请求数据转化为字典格式

### `def _save_subnet(self, context, network, subnet_args, dns_nameservers, host_routes, subnet_request)`

1. 调用 `_validate_subnet_cidr` 验证待创建子网的 `cidr` 属性是否合法
2. 调用 `_validate_network_subnetpools` 验证该子网与所属网络下的其他子网是否是在同一子网池中分配的
3. 创建一条 `Subnet` 的数据库记录
4. 调用 `_validate_segment` 验证 `segment_id` 是否满足要求
5. 若新创建的 subnet 数据中包含 `dns_namservers` 属性，则会创建 `DNSNameServer` object 实例，进一步创建数据库记录。
6. 若新创建的 subnet 数据中包含 `host_routes` 属性，则会创建 `SubnetRouter` 的数据库记录
7. 若新创建的 subnet 数据中包含 `service_types` 属性，则会创建 `SubnetServiceType` 的数据库记录
8. 调用 `save_allocation_pools` 创建 `IPAllocationPool` 的数据库记录

### `def _validate_subnet_cidr(self, context, network, new_subnet_cidr)`

1. `cidr` 的 `prefixlen` 不能为0
2. 若配置中设置 `allow_overlapping_ips` （允许不同的网络拥有重复的 ip）为 True，则获取该网络下的所有子网，否则则获取这个 openstack 中所有的子网
3. 对比上一步获取的子网列表，检查当前请求创建的子网的 `cidr` 是否和这些子网中有重复的 Ip 地址，若有则引发异常，若没有则正确返回

### `def _validate_network_subnetpools(self, network, new_subnetpool_id, ip_version)`

**neutron 中有这么一个要求，同一网络下，若是子网都是从子网池中分配的，那么则要求所有的子网都在同一子网池中分配**

### `def _validate_segment(self, context, network_id, segment_id)`

1. 根据 `network_id` 获取该网络下的所有子网记录，并获取这些字网的 `segment_id`
2. **同一网络下的所有子网要么都有 `segment_id`，要么都没有 `segment_id`**
3. **每个 `segment_id` 只能属于一个网络**

### `def delete_port(self, context, id)`

根据 id 获取 `Port` 的数据库记录，然后删除该记录

### `def update_port(self, context, old_port_db, old_port, new_port)`

1. 获取新 port 所在的主机名称
2. 调用 `update_port_with_ips` （在子类中实现的）更新 port 的 ip 地址，获取该 port 上新增、不变、删除的 Ip 地址列表
3. 判断段是否需要延迟分配 IP（`fixed_ips_requesed`）
4. 若是不需要延迟分配 ip 且只改变了 port 的 host，而没有改变 fixed_ip，则检查 port 以前的 ip 是否可以在新的 host 上分配，若不能则引发异常，若可以则返回该 port 上新增、不变、删除的 Ip 地址列表
5. 若是需要延迟分配 Ip，则调用 `allocate_ips_for_port_and_store`（子类中实现）进行 IP 的分配，返回该 port 上新增、不变、删除的 Ip 地址列表

### `def _get_changed_ips_for_port(self, context, original_ips, new_ips, device_owner)`

若 ip 有 `delete_subnet` 这条属性，则表明这个 IP 是 Ipv6 版本且是自动分配的，加上这个标识用于标识该 ip 被强制更新（请参考 `Ml2Plugin.delete_subnet`中的说明）。

1. 统计含有 `delete_subnet` 属性的 ip
2. 统计不含有 `delete_subnet` 属性的 ip
3. 调用 `_validate_max_ips_per_port` 验证该网卡是否可以分配这些 ip 地址
4. 对于要更新的 ip 地址的 port 资源来说，有这么三种情况：`add_ips`：新增的 ip 地址；`prev_ips`：之前存在但还继续使用的 IP 地址；`remove_ips`：需要被删除的 ip 地址
5. 返回上面获取的 Ip 地址的三种情况。

### `def _validate_max_ips_per_port(self, fixed_ip_list, device_owner)`

1. 调用 `common_utils.is_port_trusted` 验证该网卡是否可以访问该网络
2. `max_fixed_ips_per_port` 在 */etc/neutron/neutron.conf* 中，用于设定每个网卡可以有几个 Ip 地址

### `def _is_ip_required_by_subnet(self, context, subnet_id, device_owner)`

判断一个子网的 ip 是否需要手动设置：

1. `device_owner` 为 `const.ROUTER_INTERFACE_OWNERS_SNAT`
2. 非 ipv6 自动分配地址和地址池不为 `IPV6_PD_POOL_ID` 的子网

### `def _ipam_get_subnets(self, context, network_id, host, service_type=None)`

1. 调用 `_find_candidate_subnets`，根据网络的 id，host，service_type 获取合适的 subnet，
2. 若有合适的子网，则调用 `_make_subnet_dict`， 返回该子网字典形式的数据
3. 若没有合适的子网，则判断因为什么原因没找到合适的 subnet，并根据原因引发不同的异常

### `def _find_candidate_subnets(self, context, network_id, host, service_type)`

根据网络的 id，host，service_type 获取合适的 subnet

1. 调用 `_query_subnets_on_network` 获取一个网络下的所有子网的数据库记录
2. 调用 `_query_filter_service_subnets` 获取满足 `service_type` 的子网记录
3. 如果 `host` 参数为被设置，则调用 `_query_exclude_subnets_on_segments` 返回没有设置 `segment_id` 的子网
4. 如果设置了 `host` 参数，则调用 `_query_filter_by_segment_host_mapping` 获取可到达该 Host 的子网数据库记录，返回这个子网数据库记录

### `def _query_subnets_on_network(self, context, network_id)`

获取一个网络下的所有子网的数据库记录

### `def _query_filter_service_subnets(self, query, service_type)`

从子网的数据库记录 `query` 中获取满足 `service_type` 的子网记录

### `def _query_exclude_subnets_on_segments(query)`

从子网的数据库记录 `query` 中获取未设置 `segment_id` 的子网记录

### `def _query_filter_by_segment_host_mapping(query, host)`

根据子网的 segment_id 查询该子网可以到达的是否可以到达该 Host

### `def _get_subnet_for_fixed_ip(self, context, fixed, subnets)`

从一些候选的子网中，选择出可以分配 `fixed` ip 的子网

### `def _update_ips_for_pd_subnet(self, context, subnets, fixed_ips, mac_address=None)`

处理特殊的 ipv6 版本的地址

### `def _delete_ip_allocation(context, network_id, subnet_id, ip_address)`

对于那些从 port 上删除的 ip 地址，删除其在 `IPAllocation` 数据库上的记录

### `def _store_ip_allocation(context, ip_address, network_id, subnet_id, port_id)`

对于那些从 port 上新增的 ip 地址，增加其在 `IPAllocation` 数据库上的记录

### `def _classify_subnets(self, context, subnets)`

将子网 `subnets` 分为三类：`v4`、`v6_stateful`、`v6_stateless`

---

## `class IpamPluggableBackend(ipam_backend_mixin.IpamBackendMixin)`

### `def update_db_subnet(self, context, id, s, old_pools)`

* 参数介绍
 * `context`：
 * `id`：待更新的子网 id
 * `s`：子网的新属性
 * `old_pools`：子网之前的地址池

1. 调用父类的 `update_db_subnet` 完成与 subnet 有关的数据库的升级处理
2. 调用 `_ipam_update_allocation_pools` 更新 ipam subnet 的 `IpamAllocationPool` 数据库记录

### `def _ipam_update_allocation_pools(self, context, ipam_driver, subnet)`

1. 调用 Ipam 驱动 `ipam_driver` 来构造创建或者更新子网的请求
2. 调用 Ipam 驱动的 `update_subnet` 来更新 ipamsubnet 

## `def allocate_subnet(self, context, network, subnet, subnetpool_id)`

分配子网，参数介绍：

* `network`：该子网绑定到哪个网络之上，这里网络的数据库记录
* `subnet`：欲创建的子网的参数
* `subnetpool_id`：想要从哪个子网池中分配子网

1. 当 `subnetpool_id` 不为空且不为 `IPV6_PD_POOL_ID` 时：
 1. 调用 `_get_subnetpool` 获取 SubnetPool object 对象
 2. 调用 `_validate_ip_version_with_subnetpool` 验证待创建的子网的 ip 版本与子网池的 Ip 版本一致
2. 如果 subnet 包含了 `cidr` 属性：
 1. 调用 `_gateway_ip_str` 获取欲创建的子网的网关地址
 2. 调用 `_prepare_allocation_pools` 验证地址池是否合法，并且获得以 `IPRange` 描述的地址池
3. 调用 `driver.Pool.get_instance` 获取 ipam 驱动实例（`NeutronDbPool`） `ipam_driver`
4. 调用 `get_subnet_request_factory`、`get_request` 来构造创建子网的请求
5. 调用 `ipam_driver.allocate_subnet` 进行 IpamSubnet（注意，不是 `Subnet`） 子网的分配、创建工作
6. 调用 `_make_subnet_args` 将创建子网的请求数据 subnet 转化为详细的字典格式
7. 调用 `_save_subnet` 进行子网参数的验证以及创建 `Subnet` 的数据库记录

### `def save_allocation_pools(self, context, subnet, allocation_pools)`

创建 `IPAllocationPool` 的数据库记录

### `def add_auto_addrs_on_network_ports(self, context, subnet, ipam_subnet)`

若该子网是 ipv6 版本的，且是自动分配 IP 地址，则会调用此方法自动给该网络的 **内部port（非 `ROUTER_INTERFACE_OWNERS_SNAT` 类型？？）** 分配 Ip
 
1. 获取该网络下的所有非 `ROUTER_INTERFACE_OWNERS_SNAT` 类型的 Port
2. 获取 Ipam 的驱动实例
3. 根据每个 port 创建 ipam 中 ip 地址的分配请求，并将这个请求发送给该子网的 ipam 实例（`NeutronDbSubent` ipam_subnet）来分配 ip 地址。
4. 针对每个分配 IP 的 port 创建 `IPAllocation` 的数据库记录
5. 返回所有被更新过的 port 的 id 列表

### `def delete_subnet(self, context, subnet_id)`

1. 获取 ipam 的驱动实例 `ipam_driver`
2. 调用驱动的 `remove_subnet` 方法删除 `IpamSubnet` 的数据库记录

### `def delete_port(self, context, id)`

1. 根据 `id` 获取 `Port` 的数据库记录
2. 获取 ipam 后台驱动
3. 调用父类的 `delete_port` 删除 `Port` 数据库记录
4. 调用 `_ipam_deallocate_ips` 回收 ip 地址

### `def _ipam_deallocate_ips(self, context, ipam_driver, port, ips, revert_on_fail=True)`

删除 port 时应该调用此方法回收 Ip

1. 调用 `ipam_driver.get_subnet` 获取 Ipam subnet 实例
2. 调用 `ipam_subnet.deallocate` 回收 Ip 地址
3. 若是回收过程中发生异常且 `ipam_driver.needs_rollback()` 为真，则调用 `_ipam_allocate_ips` 将那些已经回收回来的 Ip 重新分配回去

### `def _safe_rollback(self, func, *args, **kwargs)`

```
    def _safe_rollback(self, func, *args, **kwargs):
        """Calls rollback actions and catch all exceptions.                                                                                                            
    
        All exceptions are catched and logged here to prevent rewriting
        original exception that triggered rollback action.
        """ 
        try:
            func(*args, **kwargs)
        except Exception as e:
            LOG.warning(_LW("Revert failed with: %s"), e)
```

### `def _ipam_allocate_ips(self, context, ipam_driver, port, ips, revert_on_fail=True)`

调用 `ipam_driver` 为 port 分配 Ip

### `def update_port_with_ips(self, context, host, db_port, new_port, new_mac)`

参数说明：

* `host`：待更新 port 所在的主机名称
* `db_port`： port 更新前的数据库记录
* `new_port`：port 的新数据
* `new_mac`：port 的新的 mac 地址

1. 调用 `_update_ips_for_port` 进行 ip 地址的更新（IPAM），并获取新增、不变、删除的 Ip 地址列表
2. 调用 `_delete_ip_allocation` 对那些删除的 ip 地址删除 `IPAllocation` 的数据库记录
3. 调用 `_store_ip_allocation` 对那些新增的 ip 地址增加 `IPAllocation` 的数据库记录
4. 最后调用 `_update_db_port` 更新 `Port` 数据库的记录
5. 若在以上过程中发生异常，则调用 `_ipam_deallocate_ips` 将新分配的地址回收，调用 `_ipam_allocate_ips` 将删除的地址重新分配回去
6. 返回新增、不变、删除的 Ip 地址列表


### `def _update_ips_for_port(self, context, port, host, original_ips, new_ips, mac)`

1. 调用 `_get_changed_ips_for_port` 获取该 port 上 ip 地址的变动情况
2. 调用 `_ipam_get_subnets` 获取合适的用来分配 Ip 地址的子网
3. 调用 `_test_fixed_ips_for_port` 获取每个ip以及其对应的子网的列表
4. 调用 `_update_ips_for_pd_subnet` 处理特殊的 ipv6 版本的地址
5. 调用 `_ipam_deallocate_ips` 回收那些不用的 ip 地址
6. 调用 `_ipam_allocate_ips` 分配那些更新（新增）的 ip 地址
7. 返回新增、不变、删除的 Ip 地址列表


### `def _test_fixed_ips_for_port(self, context, network_id, fixed_ips, device_owner, subnets)`

1. 调用 `_get_subnet_for_fixed_ip` 为每个 ip 选择可分配的子网
2. 调用 `_validate_max_ips_per_port` 验证该 port 的 ip 地址没有超出限制
3. 返回 ip 与其对应的子网的列表

### `def allocate_ips_for_port_and_store(self, context, port, port_id)`

1. 调用 `_allocate_ips_for_port` 


### `def _allocate_ips_for_port(self, context, port)`

1. 调用 `_ipam_get_subnets` 获取合适的用来分配 Ip 地址的子网
2. 调用 `_classify_subnets` 将刚才获取的子网分为三类：`v4`、`v6_stateful`、`v6_stateless`
3. 对于含有 `foxed_ips` 属性的 port，调用 `_test_fixed_ips_for_port` 获取可分配 Ip 地址的子网（**手动指定 ip 地址**）
4. 对于不含有 `foxed_ips` 属性的 port，则将 `v4`、`v6_stateful` 作为可分配 Ip 地址的子网（**自动分配 IP 地址**）
5. 若 port 的 `device_owner` 属性不是 `ROUTER_INTERFACE_OWNERS_SNAT`，则将 `v6_stateless` 加入到可分配你 Ip 地址的子网中
6. 调用 `_ipam_allocate_ips` 进行实际的 IP 地址分配