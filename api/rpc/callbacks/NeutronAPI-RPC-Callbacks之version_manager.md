# Neutron API RPC Callbacks 之 version_manager

*neutron/api/rpc/callbacks/version_manager.py*

## `def _get_cached_tracker()`

构造全局唯一的 `CachedResourceConsumerTracker` 实例。

## `class CachedResourceConsumerTracker(object)`

### `def __init__(self)`

```
    def __init__(self):
        # This is TTL expiration time, 0 means it will be expired at start
        self._expires_at = 0
        self._versions = ResourceConsumerTracker()
```

1. `_expires_at` ： 时间戳，用于比较该记录的过期时间
2. `_versions` : 用于存储具体追踪的资源及其版本

### `def update_versions(self, consumer, resource_versions)`

调用 `ResourceConsumerTracker.set_versions` 来实现 （参考 `AgentExtRpcCallback._update_local_agent_resource_versions` 的调用）

### `def get_resource_versions(self, resource_type)`

1. 调用 `_check_expiration`


### `def _check_expiration(self)`

若是时间戳已经过时，则调用 `_update_consumer_versions` 更新追踪资源及其版本的记录

### `def _update_consumer_versions(self)`

1. 创建新的追踪对象
2. 调用 core plugin 的 `get_agents_resource_versions` 方法来获取所有 agent 使用的资源及其版本，并用来更新追踪对象
3. 调用 `ResourceConsumerTracker.report` 来记录日志

### `def report(self)`

```
    def report(self):
        self._check_expiration()
        self._versions.report()
```

## `class ResourceConsumerTracker(object)`

### `def __init__(self)`

```
    def __init__(self):
        self._versions = self._get_local_resource_versions()
        self._versions_by_consumer = collections.defaultdict(dict)
        self._needs_recalculation = False
```

### `def _get_local_resource_versions(self)`

记录本地的资源极其版本，在 `resources.LOCAL_RESOURCE_VERSIONS` 中记录

### `def set_versions(self, consumer, versions)`

* 参数说明：
 * `consumer`：必须为 `AgentConsumer` 实例（例如：`version_manager.AgentConsumer(agent_type='Open vSwitch agent', host='localhost')`）
 * `version`：字典格式（例如 `{'QosPolicy': '1.1', 'SecurityGroup': '1.0', 'Port': '1.0'}`）

1. 调用 `_set_version` 更新 consumer 所使用的资源版本
2. 若是 verion 数据不为空，则调用 `_cleanup_removed_versions` 清除那些 consumer 不再使用的资源及其版本
3. 若是 version 数据为空，则调用 `_handle_no_set_versions` 清除该 consumer 的资源追踪记录

### ` def _set_version(self, consumer, resource_type, version)`

1. 更新本地的资源版本的记录 `self._versions`
2. 检查当前的 consumer 的资源版本是否与之前记录的资源版本一致，若是不一致则将 `_needs_recalculation` 置为 True

### `def _cleanup_removed_versions(self, consumer, versions)`

清除那些不再被追踪的资源及其版本

### `def _handle_no_set_versions(self, consumer)`

清空该 consumer 下的资源追踪记录

### `def get_resource_versions(self, resource_type)`

根据资源类型计算其版本，调用 `_recalculate_versions` 实现。重新计算完成后将 `_needs_recalculation` 置为 False

### `def _recalculate_versions(self)`

根据本地记录的资源及其版本，根据 consumer 使用的资源及其版本来更新 `self._versions` 的记录

### `def report(self)`

将 `self._versions` 以及 `self._versions_by_consumer` 输出到日志中

## `def _import_resources()`

```
def _import_resources():
    return importutils.import_module('neutron.api.rpc.callbacks.resources')
```

`neutron.api.rpc.callbacks.resources` 这个模块里面记录了当前可追踪的资源及其版本

## `def _import_agents_db()`

```
def _import_agents_db():
    return importutils.import_module('neutron.db.agents_db')
```


