# oslo_service 之 loopingcall

*oslo_service/loopingcall.py*

## `class LoopingCallBase(object)`

```
    _KIND = _("Unknown looping call")

    _RUN_ONLY_ONE_MESSAGE = _("A looping call can only run one function"
                              " at a time")
```

### `def __init__(self, f=None, *args, **kw)`

* `f` : 准备循环执行的任务
* `args`： f 的参数
* `kw`： f 的参数

```
    def __init__(self, f=None, *args, **kw):
        self.args = args
        self.kw = kw
        self.f = f
        self._running = False
        self._thread = None
        self.done = None
```


### `def stop(self)`

```
    def stop(self):
        self._running = False
```

### `def wait(self)`

```
    def wait(self):
        return self.done.wait()
```

### `def _on_done(self, gt, *args, **kwargs)`

```
    def _on_done(self, gt, *args, **kwargs):
        self._thread = None
        self._running = False
```

### `def _start(self, idle_for, initial_delay=None, stop_on_exception=True)`

* 参数说明：
 1. `idle_for`：用于计算空闲时间的方法
 2. `initial_delay`： 开始循环前的延迟时间
 3. `stop_on_exception`：发生异常时是否继续支持循环

孵化一个绿色线程 `self._thread` 来执行，这个绿色线程执行的是 `_run_loop` 方法。

### `def _run_loop(self, idle_for_func, initial_delay=None, stop_on_exception=True)`

其实就是保持 `self.f` 间隔持续的运行，间隔时间通过 `idle_for_func` 来计算

## `class FixedIntervalLoopingCall(LoopingCallBase)`

技能循环执行一个任务（方法）。

```
    _RUN_ONLY_ONE_MESSAGE = _("A fixed interval looping call can only run"
                              " one function at a time")

    _KIND = _('Fixed interval looping call')
```

### `def start(self, interval, initial_delay=None, stop_on_exception=True)`

* 参数说明：
 * `interval`：方法间隔执行的时间
 * `initial_delay`：方法开始执行时的延迟时间
 * `stop_on_exception`：发生异常时是否停止

1. 定义了一个计算延迟时间的方法 `def _idle_for(result, elapsed)`
 * **说明：**假设这个方法需要每 30 秒执行一次，但是这个方法执行的时间需要花费 20 秒，那么这次执行结束到下次执行开始的中间间隔即为 10 秒。`_idle_for` 就是为计算这个间隔时间的。
2. 调用 `_start` 开始循环执行方法。










