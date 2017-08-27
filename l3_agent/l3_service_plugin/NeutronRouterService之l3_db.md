# Neutron Router Service 之 l3_db

*neutron/db/l3_db.py*

## router and floating ip extension

*neutron/extensions/l3.py*

`RESOURCE_ATTRIBUTE_MAP` 定义了 router 和 floating ip 的属性

`class L3(extensions.ExtensionDescriptor)` 为 router 的描述，为 WSGI 构造 controller 。

`class RouterPluginBase(object)` 为 router WSGI 实现的抽象基类。


## 数据库 RouterPort、Router、FloatingIP

```
class RouterPort(model_base.BASEV2)

class Router(standard_attr.HasStandardAttributes, model_base.BASEV2,
             model_base.HasId, model_base.HasProject)

class FloatingIP(standard_attr.HasStandardAttributes, model_base.BASEV2,
                 model_base.HasId, model_base.HasProject)
```

## `class L3_NAT_db_mixin(L3_NAT_dbonly_mixin, L3RpcNotifierMixin)`


在 `L3_NAT_dbonly_mixin` 基础上的封装，`L3_NAT_db_mixin` 是负责具体逻辑业务的处理。
在 `L3_NAT_dbonly_mixin` 处理完距离的逻辑业务后，`L3_NAT_db_mixin` 来发送 RPC 消息

### `def create_router(self, context, router)`

调用 `L3_NAT_dbonly_mixin.create_router` 实现具体的业务逻辑
若新创建的 router 包含 `external_gateway_info` 属性，则调用 `notify_router_updated` （`L3RpcNotifierMixin`）发送 RPC 消息

### `def update_router(self, context, id, router)`

调用 `L3_NAT_dbonly_mixin.update_router` 实现具体的业务逻辑
调用 `notify_router_updated`（`L3RpcNotifierMixin`）发送 RPC 消息

### `def delete_router(self, context, id)`

调用 `L3_NAT_dbonly_mixin.delete_router` 实现具体的业务逻辑
调用 `notify_router_deleted`（`L3RpcNotifierMixin`）发送 RPC 消息

### `def notify_router_interface_action(self, context, router_interface_info, action)`

调用 `notify_routers_updated`（`L3RpcNotifierMixin`）发送 RPC 消息
调用 `n_rpc.get_notifier` 获取 notifier 实例，发送关于 router 的通知消息

### `def add_router_interface(self, context, router_id, interface_info)`

调用 `L3_NAT_dbonly_mixin.add_router_interface` 实现具体的业务逻辑
调用 `notify_router_interface_action` 发送 router 更新的 RPC 消息以及通知消息

### `def remove_router_interface(self, context, router_id, interface_info)`

调用 `L3_NAT_dbonly_mixin.remove_router_interface` 实现具体的业务逻辑
调用 `notify_router_interface_action` 发送 router 更新的 RPC 消息以及通知消息

### `def create_floatingip(self, context, floatingip, initial_status=lib_constants.FLOATINGIP_STATUS_ACTIVE)`

调用 `L3_NAT_dbonly_mixin.create_floatingip` 实现具体的业务逻辑
调用 `notify_router_updated`（`L3RpcNotifierMixin`）发送 RPC 消息

### `def update_floatingip(self, context, id, floatingip)`

调用 `L3_NAT_dbonly_mixin._update_floatingip` 和 `L3_NAT_dbonly_mixin._floatingips_to_router_ids` 实现具体的业务逻辑
调用 `notify_router_updated`（`L3RpcNotifierMixin`）发送 RPC 消息

### `def delete_floatingip(self, context, id)`

调用 `L3_NAT_dbonly_mixin._delete_floatingip` 实现具体的业务逻辑
调用 `notify_router_updated`（`L3RpcNotifierMixin`）发送 RPC 消息

### `def disassociate_floatingips(self, context, port_id, do_notify=True)`

调用 `L3_NAT_dbonly_mixin.disassociate_floatingips` 实现具体的业务逻辑
调用 `notify_router_updated` 发送 RPC 消息

### `def notify_routers_updated(self, context, router_ids)`

```
    def notify_routers_updated(self, context, router_ids):
        super(L3_NAT_db_mixin, self).notify_routers_updated(
            context, list(router_ids), 'disassociate_floatingips', {})
```

### `def _migrate_router_ports(self, context, router_db, old_owner, new_owner)`

```
    def _migrate_router_ports(
        self, context, router_db, old_owner, new_owner):
        """Update the model to support the dvr case of a router."""
        for rp in router_db.attached_ports.filter_by(port_type=old_owner):
            rp.port_type = new_owner
            rp.port.device_owner = new_owner
```

## `class L3_NAT_dbonly_mixin(l3.RouterPluginBase, st_attr.StandardAttrDescriptionMixin)`

l3 层中核心资源 router、router port、floating ip 的业务逻辑的实现。

```
    router_device_owners = (
        DEVICE_OWNER_HA_REPLICATED_INT,
        DEVICE_OWNER_ROUTER_INTF,
        DEVICE_OWNER_ROUTER_GW,
        DEVICE_OWNER_FLOATINGIP
    )

    _dns_integration = None
```

```
    def __new__(cls):
        L3_NAT_dbonly_mixin._subscribe_callbacks()
        return super(L3_NAT_dbonly_mixin, cls).__new__(cls)
```

### `def _subscribe_callbacks()`

```
    @staticmethod
    def _subscribe_callbacks():
        registry.subscribe(
            _prevent_l3_port_delete_callback, resources.PORT,
            events.BEFORE_DELETE)
```

注册对 `PORT` 资源事件的监测。

PORT: BEFORE_DELETE: _prevent_l3_port_delete_callback

### `def _core_plugin(self)`

返回 core plugin 实例

### `def _get_router(self, context, router_id)`

根据 id 获取一个 Router 数据库的记录

### `def _is_dns_integration_supported(self)`

判断是否支持 dns extension

### `def _make_router_dict(self, router, fields=None, process_extensions=True)`

将 router 的数据库记录改成一个易读的字典格式

### `def filter_allocating_and_missing_routers(self, context, routers)`

通过查询数据库 `Router`，过滤掉 routers 中正处于 `ALLOCATING` 状态的 router

### `def _create_router_db(self, context, router, tenant_id)`

创建一个 router 的数据库记录。

发送 router 资源准备创建的消息

### `def _check_for_external_ip_change(self, context, gw_port, ext_ips)`

根据 gateway 信息，判断其 gateway port 的 ip 地址是否要发生变化

### `def _validate_gw_info(self, context, gw_port, info, ext_ips)`

验证 gateway 的信息是否正确

1. 该 gateway 所在的 network 是否是 external network。
2. 该 gateway 的 ip 地址不能是 external nerwork subnet 的 gateway_ip

### `def _update_router_gw_info(self, context, router_id, info, router=None)`

一个 gateway info 可能如下：

```
        "external_gateway_info": {
            "enable_snat": true,
            "external_fixed_ips": [
                {
                    "ip_address": "172.24.4.6",
                    "subnet_id": "b930d7f6-ceb7-40a0-8b81-a425dd994ccf"
                }
            ],
            "network_id": "ae34051f-aa6c-4c75-abf5-50dc9ac99ef3"
        }
```

1. 调用 `_get_router` 获取当前 router 的数据库记录
2. 调用 `_check_for_external_ip_change` 判断 router 上 gateway 信息是否发生了变化
3. 调用 `_validate_gw_info` 验证 gateway 的信息是否正确
4. 若是 gateway port 存在且其 ip 发生了变化（但是 ip 所在的 network 未发生变化）则调用 `_update_current_gw_port` 更新 gateway，否则：
 1. 调用 `_delete_current_gw_port` 删除 gateway port 
 2. 调用 `_create_gw_port` 创建新的 gateway port

### `def _update_current_gw_port(self, context, router_id, router, ext_ips)`

调用 core plugin 的 update_port 方法更新 gateway port 的信息

### `def _delete_current_gw_port(self, context, router_id, router, new_network_id)`

1. 判断当前的 gateway port 是否在使用，若是在使用则引发异常
2. 更新 router 的数据看记录
3. 调用 core plugin 的 delete port 删除 gateway port
4. 通知有 gateway port 资源被删除

### `def _create_gw_port(self, context, router_id, router, new_network_id, ext_ips)`

1. 验证参数是否正确
2. 调用 core plugin 的 `get_subnets_by_network` 获取子网数据
3. 发送 gateway port 即将创建的通知
4. 调用 `_check_for_dup_router_subnets` 进行进一步的判断
5. 调用 `_create_router_gw_port` 创建 gateway port
6. 发送 gateway port 创建的通知

### `def _check_for_dup_router_subnets(self, context, router, network_id, new_subnets)`

判断同一网络上的不同 subnet 是否已经有 port 在此 router 上

### `def _create_router_gw_port(self, context, router, network_id, ext_ips)`

1. 创建 port
2. 创建 RouterPort 记录
3. 更新 router 的记录

### `def create_router(self, context, router)`

创建一个 router。

调用 `common_db_mixin.safe_creation` 来实现。

1. 创建 router 数据库
2. 调用 `_update_gw_for_create_router` 绑定 gateway 信息
3. 若 `_update_gw_for_create_router` 失败，则调用 `delete_router` 删除 router

### `def _update_gw_for_create_router(self, context, gw_info, router_id)`

为新创建的 router 创建一个 gateway（调用 `_update_router_gw_info`）。

### `def delete_router(self, context, id)`

1. 调用 `_ensure_router_not_in_use` 确保该 router 不再被使用
2. 调用 `_delete_current_gw_port` 删除 gateway port
3. 删除所有与该 router 相关联的 port
4. 发送 router 即将被删除的通知
5. 删除 router 的数据库记录

### `def _ensure_router_not_in_use(self, context, router_id)`

检查是否该 router 还在使用

### `def get_routers(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

获取多个 router 记录

### `def get_routers_count(self, context, filters=None)`

获取符合条件的 router 的数量

### `def _get_device_owner(self, context, router=None)`

返回 `DEVICE_OWNER_ROUTER_INTF`

### `def _make_router_interface_info`

创建 router interface port 的信息

### `def prevent_l3_port_deletion(self, context, port_id)`

根据 port_id 检查该 port 是否还在 L3 层被使用，若还在被使用则引发异常

### `def update_router(self, context, id, router)`

1. 若是更新的 router 信息中带有 `external_gateway_info`：
 1. 调用 `_check_router_needs_rescheduling` 检查 router 的 gw_info 发生变化时是否需要重新调度
 2. 调用 `_update_router_gw_info` 更新 router 的 gateway 信息
2. 调用 `_update_router_db` 更新数据库记录，并发送数据库更新的事件通知
3. 若是有可以与 router 重新绑定的 l3 agent（重新调度），则调用 `l3_plugin.reschedule_router` 实现 router 的重新调度
4. 返回更新后 router 的数据

### `def _check_router_needs_rescheduling(self, context, router_id, gw_info)`

1. 获取该 router 绑定的外部网络的 id 
2. 通过 ml2 获取所有的 externel network
3. 检查 l3 plugin 是否支持 l3_agent_scheduler，若不支持则退出（默认的 scheduler 驱动为：`router_scheduler_driver = neutron.scheduler.l3_agent_scheduler.LeastRoutersScheduler`）
4. 调用 `l3_plugin.router_supports_scheduling`（在 `L3RouterPlugin` 中实现） 检查该 router 是否支持调度
5. 调用 `l3_plugin.list_l3_agents_hosting_router` 找到与该 router 绑定的 l3agent
6. 若是需要重新绑定 router 与 l3 agent:
 1. 调用 `l3_plugin.get_l3_agents` 获取所有活动的 l3 agent
 2. 调用 `l3_plugin.get_l3_agent_candidates` 获取可以与该 router 绑定的 l3 agent

### `def _update_router_db(self, context, router_id, data)`

1. 更新 Router 中的数据库记录
2. 通过 neutron callback 系统发送 ROUTER 资源 PRECOMMIT_UPDATE 的事件

### `def _make_router_dict_with_gw_port(self, router, fields)`

将 router 的数据库记录数据转化为字典格式。
若 router 中包含 `gw_port` 属性，则调用 `core_plugin._make_port_dict` 将 `gw_port` 数据也转化为易读的字典格式

### `def _get_router_info_list(self, context, router_ids=None, active=None, device_owners=None)`

1. 调用 `self._get_sync_routers` 获取数据库中关于这些 router 的详细数据
2. 调用 `self._get_sync_interfaces` 获取与这些 router 绑定的 port 的详细数据
3. 调用 `_get_sync_floating_ips` 获取与这些 router 绑定的 floating ip 的详细数据
4. 返回上面获取的 router、port、floating ip 的数据

### `def _get_sync_routers(self, context, router_ids=None, active=None)`

**作用：读取数据库中关于 router 的详细信息，包括 gateway 的信息**

1. 调用 `CommonDbMixin._get_collection` 获取符合 router_ids 和 active 条件的 router 的数据
2. 读取刚才获取的 router 数据中的 `gw_port` 信息
3. 调用 `_build_routers_list`（这个方法在三个类中被实现：`L3_NAT_dbonly_mixin`、`L3_NAT_dbonly_mixin`、`L3_NAT_with_dvr_db_mixin`，我们应该以 `L3_NAT_with_dvr_db_mixin` 为最终版本） 获取 router 详细属性

### `def _build_routers_list(self, context, routers, gw_ports)`

```
    def _build_routers_list(self, context, routers, gw_ports):
        """Subclasses can override this to add extra gateway info"""
        return routers
```

### `def _get_sync_interfaces(self, context, router_ids, device_owners=None)`

1. 查询数据库 `RouterPort` 获取与 router_ids 代表的 router 绑定的 port，且这些 port 需要具有 device_owners 一致的属性
2. 调用 `core_plugin._make_port_dict` 获取这些 port 的详细信息

### `def _get_sync_floating_ips(self, context, router_ids)`

1. 查询数据 `FloatingIP`、`SubnetPool`、`Port`、`Subnet`，找到那些 router_ids 内的记录
2. 上面取出的 floating ip 记录可能会有重复的，调用 `_unique_floatingip_iterator` 使其单一化
3. 调用 `_make_floatingip_dict_with_scope` 返回 floating ip 的易读格式

### `def _unique_floatingip_iterator(query)`

floating ip 数据库查询记录 query 可能会有重复的，该方法的功能既是使其单一化


### `def _make_floatingip_dict_with_scope(self, floatingip_db, scope_id)`

```
    def _make_floatingip_dict_with_scope(self, floatingip_db, scope_id):
        d = self._make_floatingip_dict(floatingip_db)
        d['fixed_ip_address_scope'] = scope_id
        return d
```

### `def _make_floatingip_dict(self, floatingip, fields=None, process_extensions=True)`

构造 floating ip 的易读的数据格式

### `def _populate_mtu_and_subnets_for_ports(self, context, ports)`

1. 调用 `_each_port_having_fixed_ips` 获取带有 ip 地址的 port
2. 调用 `_get_mtus_by_network_list` 获取所有 network 的 mtu 值
3. 调用 `_get_subnets_by_network_list` 获取所有 network 的 subnet 数据
4. 对于所有的带有 ip 地址的 port 来说，获取其所在的 subnet 的数据、MTU 值

### `def _each_port_having_fixed_ips(ports)`

在 ports 中筛选出所有带有 Ip 的 port

### `def _get_mtus_by_network_list(self, context, network_ids)`

获取所有 network 的 mtu 值

### `def _get_subnets_by_network_list(self, context, network_ids)`

获取所有 network 的 subnet 数据（带有 `address_scope_id` 属性）

### `def _process_interfaces(self, routers_dict, interfaces)`

为 router 增加 `_interfaces` 属性

### `def get_sync_data(self, context, router_ids=None, active=None)`

1. 调用 `_get_router_info_list` 获取与 router_ids 所代表的 router 有关的详细数据（包含 port 和 floating ip）
2. 调用 `_populate_mtu_and_subnets_for_ports` 获取这些 router 上 port 的 subnet 数据和 mtu 值
3. 调用 `_process_floating_ips` 为 router 数据增加 `_floatingips` 属性
4. 调用 `_process_interfaces` 为 router 数据增加 `_interfaces` 属性

### `def _process_floating_ips(self, context, routers_dict, floating_ips)`

为 router 数据增加 `_floatingips` 属性

### `def _process_interfaces(self, routers_dict, interfaces)`

为 router 数据增加 `_interfaces` 属性

### `def _create_floatingip(self, context, floatingip, initial_status=lib_constants.FLOATINGIP_STATUS_ACTIVE)`

1. floating ip 所属的 network 必须是 external network
2. floating ip 必须是一个 ipv4 地址
3. 调用 `core_plugin.create_port` 创建一个与该 floating ip 绑定的 port
4. 调用 `_port_ipv4_fixed_ips` 判断该 port 的 fixed ip（也就是 floating ip） 是否为 ipv4 版本，若不是则引发异常
5. 创建一个 `FloatingIP` 的数据库记录
6. 调用 `_update_fip_assoc` 更新 floating ip 数据库的关于绑定 port 以及 router 的信息
7. 调用 `_is_dns_integration_supported` 判断 core plugin 是否支持 `dns-integration` extension，则调用 `_process_dns_floatingip_create_precommit`
8. 调用 `_is_dns_integration_supported` 判断 core plugin 是否支持 `dns-integration` extension，则调用 `_process_dns_floatingip_create_postcommit`
9. 调用 `_apply_dict_extend_functions` 处理 floating ip 的数据

### `def _port_ipv4_fixed_ips(self, port)`

判断该 port 的 fixed_ip 属性是否为 ipv4 版本

### `def _update_fip_assoc(self, context, fip, floatingip_db, external_port)`

1. 调用 `_check_and_get_fip_assoc` 判断该 floating ip 是否已经分配，若为分配则会获取`fip['port_id'], internal_ip_address, router_id` 属性
2. 更新该 floating ip 的数据库记录
3. 若是获取了该 floating ip 绑定的 router，则发送 `FLOATING_IP` 资源更新完毕的通知

### `def _check_and_get_fip_assoc(self, context, fip, floatingip_db)`

1. 若 fip 数据中包含 `fixed_ip_address` 属性，则必须要包含 `port_id` 属性
2. 如 fip 数据包含 `port_id` 属性，则：
 1. 调用 `_get_assoc_data` 获取该 floating ip 的 `fip['port_id'], internal_ip_address, router_id` 属性
 2. 若上一步获取的 port id 与 floating ip 数据库中的 `fixed_port_id` 一致，则直接返回
 3. 若不一致，则通过查询数据库 `FloatingIP` 判断该 floating ip 是否已经被分配，若被分配则引发异常

### `def _get_assoc_data(self, context, fip, floatingip_db)`

1. 调用 `_internal_fip_assoc_data` 获取将要与 floating ip 绑定的 Port 的信息
2. 调用 `_get_router_for_floatingip` 获取该 floating ip 所属的 router
3. 返回该 floating ip 的一些信息：`fip['port_id'], internal_ip_address, router_id`

### `def _internal_fip_assoc_data(self, context, fip, tenant_id)`

1. 调用 `core_plugin.get_port` 获取 floating ip 将要绑定的 port 的数据
2. 判断 port 所属的租户是否是 tenant_id 
3. 若 fip 中包含有 `fixed_ip_address` 属性，则：
 1. floating ip 要求 `fixed_ip_address` 必须为 ipv4 版本
 2. internal port 必须已经与 `fixed_ip_address` 绑定
4. 若 fip 中未包含 `fixed_ip_address` 属性，则：
 1. 调用 `_port_ipv4_fixed_ips` 获取该 internal port 中 ipv4 的地址
 2. 若还 port 上的 ipv4 地址有多个，则引发异常（floating ip 只能与一个 ipv4 地址对应）
5. 返回与 floating ip 绑定的 Port 的信息（`internal_port, internal_subnet_id, internal_ip_address`）

### `def _get_router_for_floatingip(self, context, internal_port, internal_subnet_id, external_network_id)`

1. 调用 `core_plugin.get_subnet` 获取与 floating ip 对应的 internal_subnet_id（floatip ip 所绑定 port 所在的 subnet 的 id） 的 subnet 数据
2. 若该 subnet 不存在 gateway 则引发异常
3. 调用 `get_router_for_floatingip` 获取该 floating ip 所属的 router

### `def get_router_for_floatingip(self, context, internal_port, internal_subnet, external_network_id)`

* 通过查询 `RouterPort`、`IPAllocation`、`Port`:
 1. 若找到 internal_subnet gateway_ip 所在的 router，则返回该 router 的 id
 2. 若找不到，则返回第一个找到的 router

### `def update_floatingip(self, context, id, floatingip)`

```
    @db_api.retry_if_session_inactive()
    def update_floatingip(self, context, id, floatingip):
        _old_floatingip, floatingip = self._update_floatingip(
            context, id, floatingip)
        return floatingip
```

### `def _update_floatingip(self, context, id, floatingip)`

1. 调用 `_get_floatingip` 获取原 floating ip 的数据
2. 调用 `_make_floatingip_dict` 将原 floating ip 数据转化为易读的字典格式
3. 调用 `core_plugin.get_port` 获取原 floating ip 绑定的 port 
4. 调用 `_update_fip_assoc` 更新 floating ip 数据库的关于绑定 port 以及 router 的信息
5. 调用 `_make_floatingip_dict` 获取更新过后的 floating ip 数据
6. 调用 `_is_dns_integration_supported` 判断 core plugin 是否支持 `dns-integration` extension，则调用 `_process_dns_floatingip_create_precommit`
7. 调用 `_is_dns_integration_supported` 判断 core plugin 是否支持 `dns-integration` extension，则调用 `_process_dns_floatingip_create_postcommit`
8. 调用 `_apply_dict_extend_functions` 处理 floating ip 的数据

### `def _floatingips_to_router_ids(self, floatingips)` 

获取 floating ip 所绑定的 router

### `def update_floatingip_status(self, context, floatingip_id, status)`

更新 floating ip 的 status 属性

### `def delete_floatingip(self, context, id)`

```
    @db_api.retry_if_session_inactive()
    def delete_floatingip(self, context, id):
        self._delete_floatingip(context, id)
```

### `def _delete_floatingip(self, context, id)`

*从逻辑上可以看出，删除 floating ip 只是删除了与之绑定的 port，并未删除 floating ip 的数据库记录*

1. 调用 `_get_floatingip` 获取 floating ip 的数据库记录
2. 调用 `_make_floatingip_dict` 获取 floating ip 的属性
3. 若支持 dns extension，则调用 `_process_dns_floatingip_delete`
4. 调用 `core_plugin.delete_port` 输出与 floating ip 绑定的 port
5. 返回 floating ip 的属性

### `def get_floatingip(self, context, id, fields=None)`

获取 floating ip 的数据库记录

### `def get_floatingips(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

获取多个 floating ip 的数据库记录

### `def delete_disassociated_floatingips(self, context, network_id)`

删除与某个 external network 上分配的所有 floating ip 记录

### `def get_floatingips_count(self, context, filters=None)`

找出满足过滤条件的 floating ip 的数量

### `def _router_exists(self, context, router_id)`

查询 router 是否存在

### `def _floating_ip_exists(self, context, floating_ip_id)`

查询 floating ip 是否存在

## `def _prevent_l3_port_delete_callback(resource, event, trigger, **kwargs)`

* 回调方法，当删除 port 资源时需要检查该 port 是否在 L3 层被使用：
 1. 检查 port 是否被分配了 floating ip
 2. 检查 port 是否与 router 想关联

1. 获取 l3plugin 实例
2. 调用 `l3plugin.prevent_l3_port_deletion` （在 `L3_NAT_dbonly_mixin` 中实现）检查该 Port 是否可以被删除

## `def _notify_routers_callback(resource, event, trigger, **kwargs)`

通知 l3 agent 有某些 router 更新

## `def _notify_subnet_gateway_ip_update(resource, event, trigger, **kwargs)`

通知 l3 agent 某个 router 的 gateway 发生了变化

## `def _notify_subnetpool_address_scope_update(resource, event, trigger, **kwargs)`

由 subnetpool address scope 的改变引起的通知 l3 agent 上 router 的更新