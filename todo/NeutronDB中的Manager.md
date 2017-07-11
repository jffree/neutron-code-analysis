# Neutron 中的 Manager

*neutron/manager.py*

## `class ManagerMeta(profiler.TracedMeta, type(periodic_task.PeriodicTasks))`

```
  class ManagerMeta(profiler.TracedMeta, type(periodic_task.PeriodicTasks)):                                                                                           
      pass
```

### `class TracedMeta(type)`

*osprofiler/profiler.py*

```

```


## `class Manager(periodic_task.PeriodicTasks)`

```
  @six.add_metaclass(ManagerMeta)
  class Manager(periodic_task.PeriodicTasks):
      __trace_args__ = {"name": "rpc"}
  
      # Set RPC API version to 1.0 by default.
      target = oslo_messaging.Target(version='1.0')
```















