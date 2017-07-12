# Neutron 中的 Manager

*neutron/manager.py*

## `class ManagerMeta(profiler.TracedMeta, type(periodic_task.PeriodicTasks))`

```
  class ManagerMeta(profiler.TracedMeta, type(periodic_task.PeriodicTasks)):                                                                                           
      pass
```

### `class TracedMeta(type)`

*osprofiler/profiler.py*

osprofiler 是实现 python 代码调优的模块，用于追踪每个方法的调用。[OpenStack osprofiler项目介绍](http://blog.csdn.net/liujiong63/article/details/59126243?utm_source=itdadao&utm_medium=referral)

### `class _PeriodicTasksMeta(type)`

*oslo_service/periodic_task.py*

`type(periodic_task.PeriodicTasks)` 即是 `class _PeriodicTasksMeta(type)`

该元类用于为类增加 `_periodic_tasks`（间隔执行的任务）和 `_periodic_spacing`（任务间隔的时间）两个属性。并根据该类下方法的属性，将任务方法增加到这两个属性中。 

## `class PeriodicTasks(object)`

*oslo_service/periodic_task.py*

```
@six.add_metaclass(_PeriodicTasksMeta)
class PeriodicTasks(object):
```

### `def __init__(self, conf)`

初始化实例的一些属性

### `def add_periodic_task(self, task)`

为实例增加间隔运行的任务。**注：** task 必须是被 `periodic_task` 修饰过的。

### `def run_periodic_tasks(self, context, raise_on_error=False)`

执行 `_periodic_tasks` 属性中的到达间隔时间的任务

## `class Manager(periodic_task.PeriodicTasks)`

```
  @six.add_metaclass(ManagerMeta)
  class Manager(periodic_task.PeriodicTasks):
      __trace_args__ = {"name": "rpc"}
  
      # Set RPC API version to 1.0 by default.
      target = oslo_messaging.Target(version='1.0')
```

### `def __init__(self, host=None)`

初始化实例属性

### `def periodic_tasks(self, context, raise_on_error=False)`

调用 `run_periodic_tasks` 执行周期性的任务

### `def init_host(self)`

未实现

### `def after_start(self)`

未实现









