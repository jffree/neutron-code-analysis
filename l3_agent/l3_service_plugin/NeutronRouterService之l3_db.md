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
 1. 调用 `_check_router_needs_rescheduling` 


### `def _check_router_needs_rescheduling(self, context, router_id, gw_info)`

1. 获取该 router 绑定的外部网络的 id 
2. 通过 ml2 获取所有的 externel network
3. 检查 l3 plugin 是否支持 l3_agent_scheduler，若不支持则退出（默认的 scheduler 驱动为：`router_scheduler_driver = neutron.scheduler.l3_agent_scheduler.LeastRoutersScheduler`）
4. 调用 `l3_plugin.router_supports_scheduling`（在 `L3RouterPlugin` 中实现） 检查该 router 是否支持调度
5. 调用 `l3_plugin.list_l3_agents_hosting_router` 找到与该 router 绑定的 l3agent
6. 若是需要重新绑定 router 与 l3 agent:
 1. 调用 `l3_plugin.get_l3_agents` 获取所有活动的 l3 agent
 2. 调用 `l3_plugin.get_l3_agent_candidates`




## `def _prevent_l3_port_delete_callback(resource, event, trigger, **kwargs)`

* 回调方法，当删除 port 资源时需要检查该 port 是否在 L3 层被使用：
 1. 检查 port 是否被分配了 floating ip
 2. 检查 port 是否与 router 想关联

1. 获取 l3plugin 实例
2. 调用 `l3plugin.prevent_l3_port_deletion` （在 `L3_NAT_dbonly_mixin` 中实现）检查该 Port 是否可以被删除








