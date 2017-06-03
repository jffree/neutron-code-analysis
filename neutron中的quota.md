# neutron 中的 quota

* neutron 中 quota 的配置模块：*neutron/conf/quota.py*
* neutron 中 quota 的 quota 管理模块：*neutron/quota/__init__.py*
* neutron 中 quota 的资源注册管理模块：*neutron/quota/resource_registry.py*
* neutron 中 quota 的资源模块：*neutron/quota/resource.py*
* neutron 中 quota 的 quota 数据库操作模块：*neutron/db/quota*
* neutron 中 quota 的WSGI接口模块：*neutron/extensions/quotasv2.py*

## 资源模块

在 neutron 中资源使用数量的跟踪有两种方式：一种是将资源的数量保存在数据库中，另一种是通过调用管理资源的插件的特定方法来获取资源的数量。

在 neutron 中，quota 同样使用特定的类（`TrackedResource`、`CountableResource`）来描述资源，这些类就会和上面获取资源使用数量的方式结合起来。

### `_count_resource(context, plugin, collection_name, tenant_id)`

通过调用插件特定的方法（`"get_%s_count" % collection_name` 或 `"get_%s" % collection_name`）获取资源的数量。

### `class BaseResource(object)`

1. neutron 中 quota 用于追踪资源的基础类，保存资源的名称、复数名、默认的 quota 值
2. `dirty` 对于通过数据库来存储资源使用数量的 quota 资源描述：若当前追踪的资源使用数量与数据库中的资源使用数量不一致则返回 True；若一致则返回 False；若资源未被追踪则返回 None。

### `class CountableResource(BaseResource)`

*这个类应该是为了兼容之前版本而保留的。*

用于描述通过特定方法来获取资源使用数量的 quota 资源描述。

* `count(self, context, plugin, tenant_id, **kwargs)`

调用对应的方法，获取资源使用数量。

### `class TrackedResource(BaseResource)`

用于描述通过数据库来获取资源使用数量的 quota 资源描述。

#### `__init__`

* `_model_class` 资源对应的模型类；
* `_dirty_tenants` 脏租户列表（这些租户触发了一个数据库的删除或插入操作），还未设置 quotausages 模型中的 `dirty` 位；
* `_out_of_sync_tenants` 未同步的资源使用个数的租户列表，但已经设置了 quotausages  `dirty` 位；

#### `def dirty(self)`

* 属性方法，返回当前保存的脏租户列表。

#### `def mark_dirty(self, context)`

* 更新资源在 quota 数据库 (`QuotaUsage`) 中的 `dirty` 位，更新 `_out_of_sync_tenants` 和 `_dirty_tenants`列表。

#### `def _db_event_handler(self, mapper, _conn, target)`

数据库事件的处理方法，更新 `_dirty_tenants` 列表。

#### `def register_events(self)`

对于资源本身的数据库，注册此数据库的插入删除事件

### `def unregister_events(self)`

解除数据库事件的注册。

### `def resync(self, context, tenant_id)`

获取资源本身数据库中的使用个数

调用 `_resync` 方法。

### `def _resync(self, context, tenant_id, in_use)`

调用 `_set_quota_usage` 更新 quota 数据库中的 `in_use` 字段。

更新 `_dirty_tenants` 、`_out_of_sync_tenants`属性。

### `def _set_quota_usage(self, context, tenant_id, in_use)`

更新数据库 `in_use` 字段。

### `def count(self, context, _plugin, tenant_id, resync_usage=True)`

计算当前资源的使用数量（包括保留数量）

保留数量是指正在创建中的资源个数（在创建网络时，会先 quota 的 `Reservation` 创建一个保留数据，网络创建完成后再删除）。

若 quota 数据库（`QuotaUsage`）有 `dirty` 位存在的话，则会进行同步操作，更新数据库中 `dirty` 和 `in_use` 的值。

## 注册管理模块

### 资源注册追踪 `class tracked_resources`

```
class tracked_resources(object):
    """Decorator for specifying resources for which usage should be tracked.

    A plugin class can use this decorator to specify for which resources
    usage info should be tracked into an appropriate table rather than being
    explicitly counted.
    """

    def __init__(self, override=False, **kwargs):
        self._tracked_resources = kwargs
        self._override = override

    def __call__(self, f):

        @six.wraps(f)
        def wrapper(*args, **kwargs):
            registry = ResourceRegistry.get_instance()
            for resource_name in self._tracked_resources:
                registry.set_tracked_resource(
                    resource_name,
                    self._tracked_resources[resource_name],
                    self._override)
            return f(*args, **kwargs)

        return wrapper
```

`tracked_resources` 是一个装饰器类，`_tracked_resources` 用于注册需要追踪的资源。

`tracked_resources` 的 `__call__` 既是往 `ResourceRegistry` 的实例中注册待追踪的资源。

`ResourceRegistry` 是一个全局具有唯一实例的类，用于对追踪资源的处理。

这个装饰类在 `ML2Plugin` 和 `L3RouterPlugin` 的初始化（`__init__`）时 中用到。

### 资源注册管理 `class ResourceRegistry`

这个类是 neutron 中 quota 实现的大管家。

#### `get_instance`

* 通过这个方法获取该类的实例，这个方法保证了在 neutron 的运行期间只有一个该类的实例。

#### `__init__`

1. `_resources` 属性：字典，用于保存资源名称和quota中资源实例（`TrackedResource` 或 `CountableResource`）的映射；（所有追踪资源的集合）
2. `_tracked_resource_mappings` 属性：字典，保存资源名称与其数据库实现类的映射

#### `set_tracked_resource(self, resource_name, model_class, override=False)`

* 更新实例中 `_resources` 和 `_tracked_resource_mappings` 属性。

#### `def is_tracked(self, resource_name)`

* 根据资源名称，判断该资源是否被追踪

#### `def register_resource(self, resource)`

* 再该实例中注册一个被 quota 描述的资源，同时调用该资源描述的 `register_events` 注册数据库监听事件。

#### `def register_resources(self, resources)`

* 在该实例中注册多个被 quota 描述的资源（循环调用 `register_resource`）

#### `def _create_resource_instance(self, resource_name, plural_name)`

* 通过资源名称和资源复数名称创建 quota 中描述资源的实例（`TrackedResource`、`CountableResource）。

#### `def register_resource_by_name(self, resource_name, plural_name=None):`

* 通过资源名称在 quota 中注册追踪的资源（先创建再追踪）

#### `def unregister_resources(self)`

* 取消所有的资源的监听事件，取消所有注册的资源。

#### `def get_resource(self, resource_name)`

* 通过资源名称获取 quota 中资源的描述实例

#### `def resources(self)`

* 属性方法，返回 quota 中追踪的所有资源的名称。

### 在 `ResourceRegistry` 实例上抽象出来的方法

#### `def register_resource(resource)`

* 调用 `ResourceRegistry` 实例的 `register_resource` 方法来注册追踪的资源。

#### `def register_resource_by_name(resource_name, plural_name=None)` 

* 调用 `ResourceRegistry` 的 `register_resource_by_name` 方法通过资源名称来注册资源

#### `def get_all_resources`

* 返回 `ResourceRegistry` 实例中追踪的所有资源名称


#### `def get_resource(resource_name)`

* 注销所有 `ResourceRegistry` 的追踪资源

#### `def is_tracked(resource_name)`

* 根据资源名称判断一个资源是否被追踪。

#### `def set_resources_dirty(context)`

对于所有跟踪的资源，若有的资源接收到了数据库的删除或插入事件，则会更新其本身的 `_dirty_tenants`列表。

本方法则是根据请求的上下文，更新所有跟踪资源（根据其 `_dirty_tenants` 列表）数据库（`QuotaUsage`）中的 `dirty` 位。

#### `def resync_resource(context, resource_name, tenant_id)`

更新资源被租户的使用量。

#### `def mark_resources_dirty(f)`

装饰器，对 `resync_resource` 的封装。

## quota 的管理模块

### `class ConfDriver(object)`

已废弃，被 `neutron.db.quota.driver.DbQuotaDriver` 取代。

`` 是与 quota 数据库沟通的驱动类。

### `class QuotaEngine(object)` 

这个类是 quota 的管理类，admin 可以为每个用户设定配额，配额的设定就是通过这个类来的。

#### `def get_instance(cls)`

* 保证这个类只有唯一的实例。

#### `def __init__(self, quota_driver_class=None)`

初始化函数。

#### `def get_driver(self)`

获取 quota 跟数据库沟通的驱动实例，并将实例保存至 `self._driver` 中。

#### `def count(self, context, resource_name, *args, **kwargs)`

根据请求的上下文和资源的名称获取资源的使用数量。

#### `def make_reservation(self, context, tenant_id, deltas, plugin)`

在这里做配额检查，同时创建一个 `Reservation` 数据记录。

#### `def commit_reservation(self, context, reservation_id)`

根据 `reservation_id` 删除一个 `Reservation` 记录。

#### `def cancel_reservation(self, context, reservation_id)`

根据 `reservation_id` 删除一个 `Reservation` 记录，同时将 `QuotaUsage` 的 `dirty` 置位。

#### `def limit_check(self, context, tenant_id, **values)`

检查某一资源的使用是否超限。超限则会引发异常。

## quota 中的驱动管理模块 

实现：*neutron/db/quota/driver.py* 中的 `class DbQuotaDriver(object)`

### `def get_default_quotas(context, resources, tenant_id)`

获取 resources 列表中各个资源的默认 quota 值。

### `def get_tenant_quotas(context, resources, tenant_id)`

根据 `tenant_id` 获取 `resources` 中资源的的配额，没有设定配额的返回默认值。

### `def delete_tenant_quota(context, tenant_id)`

在数据库（`Quota`）中删除某一用户的配额设定

### `def get_all_quotas(context, resources)`

获取所有资源的配额设定

### `def update_quota_limit(context, tenant_id, resource, limit)`

更新某一个租户关于某一个资源的 quota 设定

### `def _get_quotas(self, context, tenant_id, resources)`

获取某一租户关于某个资源的 quota 设定

### `def _handle_expired_reservations(self, context, tenant_id)`

处理 quota 数据库（`Reservation`）中的过期数据。

该方法在 `make_reservation` 中调用。

### `def make_reservation(self, context, tenant_id, resources, deltas, plugin)`

在 `Reservation` 数据库添加一条记录作为资源的保留项来记录。（一般意味着该资源正在创建）

### `def commit_reservation(self, context, reservation_id)`

移除 `Reservation` 数据库中的一条保留项，但是不在为改资源设置 `dirty` 位。

### `def cancel_reservation(self, context, reservation_id)`

移除 `Reservation` 数据库中的一条保留项，同时为改资源设置 `dirty` 位。

### `def limit_check(self, context, tenant_id, resources, values)`

根据传递来的 values（一般是即将创建的资源名称及其个数的映射） 检查某一租户下的某一资源的 quota 是否超限。

# 总结：

## 添加 quota 的配置

在导入 *neuton/quota* 模块是会自动运行 *__init__.py* 中的下面代码：

```
quota.register_quota_opts(quota.core_quota_opts)
```

实现添加 quota 的配置。

## 资源的注册

### `register_resource_by_name`

在 neutron 中使用 quota，需要为所有准备追踪的资源进行注册，注册的方法既是在 *neutron/quota/resource_registery.py* 中的 `register_resource_by_name` 方法。

这个方法会在下面的地方调用：

1. 在 *neutron/api/v2/router.py* 中 `APIRouter.__init__` 方法中，为 `network`、`subnet`、`subnetpool`、`port` 建立资源追踪。

2. 在 *neutron/api/v2/resource_helper.py* 中 `build_resource_info` 方法（这个方法会在 extension 的 `get_resources` 中调用，用于抛出新的资源接口）中，注册追踪 extension 提供的新资源。

3. 在 *neutron/extensions/rbac.py* 中被调用，同样是在该 extension 提供扩展资源时为其建立跟踪。

4. 在 *neutron/extensions/securitygroup.py*中被调用，同样是在该 extension 提供扩展资源时为其建立跟踪。

5. 在 *neutron/pecan_wsgi/startup.py* 中被调用，这里的调用同在 `APIRouter` 中的调用是一致的，两种不同的 WSGI 服务（启动 neutron server 时会选择一种）。

`register_resource_by_name` 会进一步调用 `ResourceRegistry.register_resource_by_name`。

### `ResourceRegistry.register_resource_by_name`

创建 quota 的一个资源描述实例，调用 `ResourceRegistry.register_resource` 方法。

### `ResourceRegistry.register_resource`

为数据库类型的资源调用 `TrackedResource.register_events` 建立事件追踪。

更新追踪管理类 `TrackedResource` 的 `_sources` 属性。

### `TrackedResource.register_events`

注册数据库的插入删除事情，事件发生后由 `TrackedResource._db_event_handler` 处理

### `TrackedResource._db_event_handler`

当有数据库事件（插入删除）时，会交由这个方法处理。

该方法会更新 `_dirty_tenants` 属性（将触发数据库动作的 `tenant_id`记录下来）

## quota 资源的追踪

quota 资源的追踪分为两部分：第一部分为当资源的数据库发生插入和删除动作时更新 quota 数据库（`QuotaUsage`）中的 `dirty` 位；第二部分为根据 quota 数据库（`QuotaUsage`）中的 `dirty` 位更新资源的使用数量 `in_use` 位。

**注意：**资源是不变的，变化的是使用资源的租户。

### 第一部分：更新 dirty

这个是有 `set_resources_dirty` 方法来完成的。它在下面几个地方被调用：

1. *neutron/api/v2/base.py* 中的 `Controller` 类中的 `_delete` 方法。
2. *neutron/api/v2/base.py* 中的 `Controller` 类中的 `_handle_action` 方法。
3. *neutron/api/v2/base.py* 中的 `Controller` 类中的 `_update` 方法。
4. *neutron/api/v2/base.py* 中的 `Controller` 类中的 `_create` 方法。

这些方法都是在调用 plugin 的方法处理完后调用的，也就是在资源数据库发生插入或删除方法后调用的。

### 第二部分，更新 in_use

更新了数据库的 `dirty` 位后不是立马更新 `in_use` 位的。

更新方法是 `def resync_resource(context, resource_name, tenant_id)`。

这个方法在下面的地方被调用：

* *neutron/api/v2/base.py* 中的 `Controller` 类中的 `_items` 方法。

## quota的注册

neutron 是如何实现为某个租户注册一个配额限制的呢？

答案是：在 *neutron/extensions/quotasv2.py* 中实现的！

`class Quotasv2(extensions.ExtensionDescriptor)` 提供了访问 quota 的接口。

`class QuotaSetsController(wsgi.Controller)` 则实现了访问 quota 时用到的 wsgi controller。

### `class QuotaSetsController(wsgi.Controller)`

#### `__init__`

初始化方法：设定关联的 plugin，设定驱动

#### `def create(self, request, body=None)`

说明不支持 create

#### `def index(self, request)`

GET 方法访问 `/v2.0/quotas` 时响应，返回所有资源的 quota 设定

#### `def show(self, request, id)`

GET 方法访问 `/v2.0/quotas/{project_id}` 时响应，返回某一租户（`id`）的 quota 设定

#### `def tenant(self, request)`

GET 方法访问 `/v2.0/quotas/tenant` 时响应，获取访问租户的 `tenant_id`

#### `def _check_admin(self, context, reason=_("Only admin can view or configure quota")):`

检测访问用户是否是 admin，不是的话引发异常

#### `def delete(self, request, id)`

使用 delete 方法访问 `/v2.0/quotas/{project_id}`时响应，删除某个租户的 quota 设定

#### `def update(self, request, id, body=None)`

使用 PUT 方法访问 `/v2.0/quotas/{project_id}`时响应，更新某个租户的 quota 设定
