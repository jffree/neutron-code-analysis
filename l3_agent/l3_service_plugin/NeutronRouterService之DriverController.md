# Neutron L3 Plugin 之 DriverController

在 `L3RouterPlugin` 初始化是会创建一个 `DriverController` 实例

*neutron/service/l3_router/service_providers/driver_controller.py*

作用：**根据 router 的类型，为其找到合适的 provider driver，并在数据库 `ProviderResourceAssociation` 中记录 router id 与 driver name 的绑定**

## `class DriverController(object)`

```
    def __init__(self, l3_plugin):
        self.l3_plugin = l3_plugin
        self._stm = st_db.ServiceTypeManager.get_instance()
        self._stm.add_provider_configuration(
                constants.L3_ROUTER_NAT, _LegacyPlusProviderConfiguration())
        self._load_drivers()
        registry.subscribe(self._set_router_provider,
                           resources.ROUTER, events.PRECOMMIT_CREATE)
        registry.subscribe(self._update_router_provider,
                           resources.ROUTER, events.PRECOMMIT_UPDATE)
        registry.subscribe(self._clear_router_provider,
                           resources.ROUTER, events.PRECOMMIT_DELETE)
```

1. 创建一个 `ServiceTypeManager` 的实例
2. 调用 `ServiceTypeManager.add_provider_configuration` 为 `L3_ROUTER_NAT` 增加一个配置实例
3. 调用 `_load_drivers` 加载所有的 provider driver
4. 对感兴趣的资源注册监听事件：
 1. router : PRECOMMIT_CREATE : _set_router_provider
 2. router : PRECOMMIT_UPDATE : _update_router_provider
 3. router : PRECOMMIT_DELETE : _clear_router_provider


### `def _load_drivers(self)`

调用 `service_base.load_drivers` 加载所有的 provider driver

### `def _flavor_plugin(self)`

获取 FLAVORS plugin 实例

### `def _set_router_provider(self, resource, event, trigger, context, router, router_db, **kwargs)`

1. 调用 `_flavor_specified` 检查 router 数据中是否包含 `flavor_id` 属性
2. 调用 `_get_provider_for_create` 获取能处理 router 属性的 provider service driver
3. 调用 `_ensure_driver_supports_request` 检查上一步获取的 driver 是否支持当前的 ha 和 distributed 的属性设定
4. 调用 `ServiceTypeManager.add_resource_association` 创建数据库的记录（将 driver name 和 router id 绑定）

### `def _get_provider_for_create(self, context, router)`

1. 若 router 数据不包含 `flavor_id` 属性，则调用 `_attrs_to_driver` 根据 ha 和 distributed 属性获取合适的 service provider driver
2. 若 router 数据包含 `flavor_id` 属性，则调用 `_get_l3_driver_by_flavor` 获取支持 flavor 操作的 driver

### `def _attrs_to_driver(self, router)`

1. 调用 `_is_distributed` 判断 router 中是否包含 `distributed` 属性
2. 调用 `_is_ha` 判断 router 中是否包含 `ha` 属性
3. 调用 `_is_driver_compatible` 查找到支持当前属性的 driver，若查找不到则引发异常

### `def _get_l3_driver_by_flavor(self, context, flavor_id)`

调用 flavor plugin 的相关方法获取支持 flavor 相关操作的 driver

#### `def _clear_router_provider(self, resource, event, trigger, context, router_id, **kwargs)`

调用 `ServiceTypeManager.del_resource_associations` 删除数据库的记录（与 router id 绑定的记录）

### `def _update_router_provider(self, resource, event, trigger, context, router_id, router, old_router, router_db, **kwargs)`

1. 调用 `_get_provider_for_router` 获取与该 router 相关联的 service provider driver
2. router 不支持 flavor id 的更新
3. 调用 `_ensure_driver_supports_request` 判断更新前为该 router 绑定的 driver 是否支持新 router 的属性，若不支持，则：
 1. 调用 `_attrs_to_driver` 为新的 router 数据找到和是的 driver
 2. 删除之前在数据库中的绑定记录，创建新的绑定记录

### `def _get_provider_for_router(self, context, router_id)`

先查询数据库是否有为该 router 绑定过 provider driver，若有的话则返回，若没有的话则查找到合适的并创建数据库记录

### `def uses_scheduler(self, context, router_id)`

根据支持该 router 的 driver，判断该 router 是否支持调度

## `def load_drivers(service_type, plugin)`

1. 调用 `ServiceTypeManager.get_service_providers` 获取该 service_type 的 provider
2. 根据获取的 provider 导入其 driver 
3. 调用 `ServiceTypeManager.get_default_service_provider` 获取其默认的 provider 名称

