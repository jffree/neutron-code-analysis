# Neutron Agent SimpleInterfaceMonitor

*neutron/agent/linux/ovsdb_monitor.py*

## `class OvsdbMonitor(async_process.AsyncProcess)`

```
class OvsdbMonitor(async_process.AsyncProcess):
    """Manages an invocation of 'ovsdb-client monitor'."""

    def __init__(self, table_name, columns=None, format=None,
                 respawn_interval=None):

        cmd = ['ovsdb-client', 'monitor', table_name]
        if columns:
            cmd.append(','.join(columns))
        if format:
            cmd.append('--format=%s' % format)
        super(OvsdbMonitor, self).__init__(cmd, run_as_root=True,
                                           respawn_interval=respawn_interval,
                                           log_output=True,
                                           die_on_error=True)
```

构造 `ovsdb-client monitor ` cmd

## `class SimpleInterfaceMonitor(OvsdbMonitor)`

```
    def __init__(self, respawn_interval=None):
        super(SimpleInterfaceMonitor, self).__init__(
            'Interface',
            columns=['name', 'ofport', 'external_ids'],
            format='json',
            respawn_interval=respawn_interval,
        )
        self.new_events = {'added': [], 'removed': []}
```

构造的 cmd 为：

```
ovsdb-client monitor Interface name,ofport,external_ids --format json
```

### `def start(self, block=False, timeout=5)`

```
    def start(self, block=False, timeout=5):
        super(SimpleInterfaceMonitor, self).start()
        if block:
            with eventlet.timeout.Timeout(timeout):
                while not self.is_active():
                    eventlet.sleep()
```

在 `AsyncProcess.start` 的基础上增加了超时检测

### `def process_events(self)`

读取 cmd 的返回值，并解析当前发生变动的 device 

### `def get_events(self)`

调用 `process_events` 获取当前发生变动的 device








