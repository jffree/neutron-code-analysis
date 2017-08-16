# Neutron router extension

*neutron/extensions/l3.py*

`RESOURCE_ATTRIBUTE_MAP` 定义了 router 的属性

`class L3(extensions.ExtensionDescriptor)` 为 router 的描述，为 WSGI 构造 controller 。

`class RouterPluginBase(object)` 为 router WSGI 实现的抽象基类。


## `class ExtraRoute_db_mixin(ExtraRoute_dbonly_mixin, l3_db.L3_NAT_db_mixin)`

```
class ExtraRoute_db_mixin(ExtraRoute_dbonly_mixin, l3_db.L3_NAT_db_mixin):
    """Mixin class to support extra route configuration on router with rpc."""
    pass
```

## `class ExtraRoute_dbonly_mixin(l3_db.L3_NAT_dbonly_mixin)`










## `class L3_NAT_dbonly_mixin(l3.RouterPluginBase, st_attr.StandardAttrDescriptionMixin)`

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

### `def _core_plugin(self)`

返回 core plugin 实例

### `def _get_router(self, context, router_id)`

根据 id 获取一个 Router 数据库的记录

### `ef _is_dns_integration_supported(self)`



### `def _make_router_dict(self, router, fields=None, process_extensions=True)`

将 router 的数据库记录改成一个易读的字典格式

### `def filter_allocating_and_missing_routers(self, context, routers)`



### `def _create_router_db(self, context, router, tenant_id)`

创建一个 router 的数据库记录。

发送 router 资源准备创建的消息

### `def _update_gw_for_create_router(self, context, gw_info, router_id)`

根据 gateway 的信息 更新router

### `def _check_for_external_ip_change(self, context, gw_port, ext_ips)`

根据 gateway 信息，判断其 gateway port 的 ip 地址是否要发生变化

### `def _validate_gw_info(self, context, gw_port, info, ext_ips)`

验证 gateway 的信息是否正确

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
4. 若是 gateway port 存在且其 ip 发生了变化则调用 `_update_current_gw_port` 更新 gateway，否则：
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
3. 检查 l3 plugin 是否支持 l3_agent_scheduler，若不支持则退出
4. 调用 `l3_plugin.router_supports_scheduling`（在 `L3RouterPlugin` 中实现） 检查该 router 是否支持调度
5. 调用 `l3_plugin.list_l3_agents_hosting_router`





## `def _prevent_l3_port_delete_callback(resource, event, trigger, **kwargs)`

* 回调方法，当删除 port 资源时需要检查该 port 是否在 L3 层被使用：
 1. 检查 port 是否被分配了 floating ip
 2. 检查 port 是否与 router 想关联

1. 获取 l3plugin 实例
2. 调用 `l3plugin.prevent_l3_port_deletion` （在 `L3_NAT_dbonly_mixin` 中实现）检查该 Port 是否可以被删除








