# neutron 中的 quota

* neutron 中 quota 的配置模块：*neutron/conf/quota.py*
* neutron 中 quota 的管理模块：*neutron/quota/__init__.py*
* neutron 中 quota 的注册模块：*neutron/quota/resource_registry.py*
* neutron 中 quota 的资源模块：*neutron/quota/resource.py*
* neutron 中 quota 的数据库操作模块：*neutron/db/quota*

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

* `_model_class` 资源对应的模型类
* `_dirty_tenants` 未更新
* `_out_of_sync_tenants` 未同步

#### ``



## 注册模块

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








