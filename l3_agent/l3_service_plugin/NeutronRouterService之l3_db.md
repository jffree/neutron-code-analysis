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

## `class ExtraRoute_dbonly_mixin(l3_db.L3_NAT_dbonly_mixin)`


在 `L3_NAT_dbonly_mixin` 基础上的封装，`L3_NAT_dbonly_mixin` 是负责具体逻辑业务的处理。
在 `L3_NAT_dbonly_mixin` 处理完距离的逻辑业务后，`ExtraRoute_dbonly_mixin` 来发送 RPC 消息

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



### `def _make_router_dict(self, router, fields=None, process_extensions=True)`

将 router 的数据库记录改成一个易读的字典格式

### `def filter_allocating_and_missing_routers(self, context, routers)`



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

## `def _prevent_l3_port_delete_callback(resource, event, trigger, **kwargs)`

* 回调方法，当删除 port 资源时需要检查该 port 是否在 L3 层被使用：
 1. 检查 port 是否被分配了 floating ip
 2. 检查 port 是否与 router 想关联

1. 获取 l3plugin 实例
2. 调用 `l3plugin.prevent_l3_port_deletion` （在 `L3_NAT_dbonly_mixin` 中实现）检查该 Port 是否可以被删除

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
