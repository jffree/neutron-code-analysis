# Neutron Agent Poll

## `class InterfacePollingMinimizer(base_polling.BasePollingManager)`

*neutron/agent/linux/polling.py*

```
    def __init__(
            self,
            ovsdb_monitor_respawn_interval=constants.DEFAULT_OVSDBMON_RESPAWN):

        super(InterfacePollingMinimizer, self).__init__()
        self._monitor = ovsdb_monitor.SimpleInterfaceMonitor(
            respawn_interval=ovsdb_monitor_respawn_interval)
````

创建一个 `ovsdb-client monitor Interface name,ofport,external_ids --format json` 的包装类 `SimpleInterfaceMonitor` 的实例

### `def start(self)`

启动 `ovsdb-client monitor Interface name,ofport,external_ids --format json` 命令

### `def stop(self)`

停止对 ovsdb Interface 的监测

### `def _is_polling_required(self)`

通过对 `ovsdb-client monitor Interface name,ofport,external_ids --format json` 命令，若发现 ovsdb 有了显得变化则返回 True，否则返回 False

### `def get_events(self)`

返回 ovsdb Interface 发生的变动

## `class BasePollingManager(object)`

*neutron/agent/common/base_polling.py*

```
    def __init__(self):
        self._force_polling = False
        self._polling_completed = True
```

```
class BasePollingManager(object):

    def __init__(self):
        self._force_polling = False
        self._polling_completed = True

    def force_polling(self):
        self._force_polling = True

    def polling_completed(self):
        self._polling_completed = True

    def _is_polling_required(self):
        raise NotImplementedError()

    @property
    def is_polling_required(self):
        # Always consume the updates to minimize polling.
        polling_required = self._is_polling_required()

        # Polling is required regardless of whether updates have been
        # detected.
        if self._force_polling:
            self._force_polling = False
            polling_required = True

        # Polling is required if not yet done for previously detected
        # updates.
        if not self._polling_completed:
            polling_required = True

        if polling_required:
            # Track whether polling has been completed to ensure that
            # polling can be required until the caller indicates via a
            # call to polling_completed() that polling has been
            # successfully performed.
            self._polling_completed = False

        return polling_required
```

## `class AlwaysPoll(BasePollingManager)`

```
class AlwaysPoll(BasePollingManager):

    @property
    def is_polling_required(self):
        return True
```


