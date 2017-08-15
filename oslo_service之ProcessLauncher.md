# oslo_service 之 ProcessLauncher

*oslo_service/service.py*

## `class ServiceWrapper(object)`

```
class ServiceWrapper(object):
    def __init__(self, service, workers):
        self.service = service
        self.workers = workers
        self.children = set()
        self.forktimes = []
```

*这是对一个 service 启动的包装类*

* `service`：待启动服务的实例
* `workers`：这个服务准备启动多少个进程
* `children`：当前已经启动的子进程的 pid
* `forktimes`：fork 操作的时间戳

## `class Singleton(type)`

```
class Singleton(type):
    _instances = {}
    _semaphores = lockutils.Semaphores()

    def __call__(cls, *args, **kwargs):
        with lockutils.lock('singleton_lock', semaphores=cls._semaphores):
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(
                    *args, **kwargs)
        return cls._instances[cls]`
```

这是个继承了 type 的元类。

在这个元类的 `__call__` 方法中，只会创建一个类。

## `class SignalHandler(object)`

```
@six.add_metaclass(Singleton)
class SignalHandler(object):

    def __init__(self, *args, **kwargs):
        super(SignalHandler, self).__init__(*args, **kwargs)
        # Map all signal names to signal integer values and create a
        # reverse mapping (for easier + quick lookup).
        self._ignore_signals = ('SIG_DFL', 'SIG_IGN')
        self._signals_by_name = dict((name, getattr(signal, name))
                                     for name in dir(signal)
                                     if name.startswith("SIG")
                                     and name not in self._ignore_signals)
        self.signals_to_name = dict(
            (sigval, name)
            for (name, sigval) in self._signals_by_name.items())
        self._signal_handlers = collections.defaultdict(set)
        self.clear()
```

1. `_signals_by_name`：信号名称到信号数字的映射
2. `signals_to_name`：信号数字到信号名称的映射
3. `_signal_handlers`：用于存放已经分配了处理方法的信号
3. 调用 `clear`

关于 signal 的相关最是请参考：[Python模块之信号（signal）](http://www.cnblogs.com/madsnotes/articles/5688681.html)

### `def clear(self)`

1. 解除 `_signal_handlers` 中对信号的绑定
2. 清空 `_signal_handlers`

### `def add_handlers(self, signals, handler)`

调用 `add_handler` 将多个信号绑定在一个处理方法上

### `def is_signal_supported(self, sig_name)`

判断是否支持该信号的处理

### `def add_handler(self, sig, handler)`

1. 调用 `is_signal_supported` 判断是否支持对信号 sig 的处理
2. 在 `_signal_handlers` 中增加 signal 与处理方法的绑定
3. 调用 `signal.signal` 将 signal 与 `_handle_signal` 进行绑定

### `def _handle_signal(self, signo, frame)`

```
eventlet.spawn(self._handle_signal_cb, signo, frame)
```

通过孵化一个绿色线程，并在线程中调用 `_handle_signal_cb` 来处理信号

### `def _handle_signal_cb(self, signo, frame)`

```
    def _handle_signal_cb(self, signo, frame):
        for handler in self._signal_handlers[signo]:
            handler(signo, frame)
```

调用绑定的方法去处理该信号。

## `class ProcessLauncher(object)`

以多进程的方式启动服务。

### ` def __init__(self, conf, wait_interval=0.01, restart_method='reload')`

```
    def __init__(self, conf, wait_interval=0.01, restart_method='reload'):
        """Constructor.

        :param conf: an instance of ConfigOpts
        :param wait_interval: The interval to sleep for between checks
                              of child process exit.
        :param restart_method: If 'reload', calls reload_config_files on
            SIGHUP. If 'mutate', calls mutate_config_files on SIGHUP. Other
            values produce a ValueError.
        """
        self.conf = conf
        conf.register_opts(_options.service_opts)
        self.children = {}
        self.sigcaught = None
        self.running = True
        self.wait_interval = wait_interval
        self.launcher = None
        rfd, self.writepipe = os.pipe()
        self.readpipe = eventlet.greenio.GreenPipe(rfd, 'r')
        self.signal_handler = SignalHandler()
        self.handle_signal()
        self.restart_method = restart_method
        if restart_method not in _LAUNCHER_RESTART_METHODS:
            raise ValueError(_("Invalid restart_method: %s") % restart_method)
```

1. 创建一个管道
2. 创建一个 `SignalHandler` 实例
3. 调用 `handle_signal` 与信号绑定处理方法


### `def handle_signal(self)`

```
    def handle_signal(self):
        """Add instance's signal handlers to class handlers."""
        self.signal_handler.add_handler('SIGTERM', self._handle_term)
        self.signal_handler.add_handler('SIGHUP', self._handle_hup)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)
        self.signal_handler.add_handler('SIGALRM', self._on_alarm_exit)
```

### `def _handle_term(self, signo, frame)`

用于处理 `SIGTERM` 信号。

*SIGTERM是杀或的killall命令发送到进程默认的信号。它会导致一过程的终止，但是SIGKILL信号不同，它可以被捕获和解释（或忽略）的过程。因此，SIGTERM类似于问一个进程终止可好，让清理文件和关闭。因为这个原因，许多Unix系统关机期间，初始化问题SIGTERM到所有非必要的断电过程中，等待几秒钟，然后发出SIGKILL强行终止仍然存在任何这样的过程。*

```
    def _handle_term(self, signo, frame):
        """Handle a TERM event.

        :param signo: signal number
        :param frame: current stack frame
        """
        self.sigcaught = signo
        self.running = False

        # Allow the process to be killed again and die from natural causes
        self.signal_handler.clear()
```

### `def _handle_hup(self, signo, frame)`

处理 `SIGHUP` 信号

[SIGHUP信号与控制终端 ](http://blog.csdn.net/cugxueyu/article/details/2046565)

```
    def _handle_hup(self, signo, frame):
        """Handle a HUP event.

        :param signo: signal number
        :param frame: current stack frame
        """
        self.sigcaught = signo
        self.running = False

        # Do NOT clear the signal_handler, allowing multiple SIGHUPs to be
        # received swiftly. If a non-HUP is received before #wait loops, the
        # second event will "overwrite" the HUP. This is fine.
```

### `def _fast_exit(self, signo, frame)`

处理 `SIGINT` 信号

*符合POSIX平台，信号情报是由它的控制终端，当用户希望中断该过程发送到处理的信号。通常ctrl-C，但在某些系统上，“删除”字符或“break”键 - 当进程的控制终端的用户按下中断正在运行的进程的关键SIGINT被发送。*

```
    def _fast_exit(self, signo, frame):
        LOG.info(_LI('Caught SIGINT signal, instantaneous exiting'))
        os._exit(1)
```

### `def _on_alarm_exit(self, signo, frame)`

处理 `SIGALRM` 信号。

*系统调用alarm安排内核为调用进程在指定的seconds秒后发出一个SIGALRM的信号。*

```
    def _on_alarm_exit(self, signo, frame):
        LOG.info(_LI('Graceful shutdown timeout exceeded, '
                     'instantaneous exiting'))
        os._exit(1)
```

### `def launch_service(self, service, workers=1)`

**本类的入口方法，以多进程的方式启动 service**

```
    def launch_service(self, service, workers=1):
        """Launch a service with a given number of workers.

       :param service: a service to launch, must be an instance of
              :class:`oslo_service.service.ServiceBase`
       :param workers: a number of processes in which a service
              will be running
        """
        _check_service_base(service)
        wrap = ServiceWrapper(service, workers)

        LOG.info(_LI('Starting %d workers'), wrap.workers)
        while self.running and len(wrap.children) < wrap.workers:
            self._start_child(wrap)
```

* `workers` : 准备为该 service 启动几个进程

调用 `_start_child` 方法实现

### `def _start_child(self, wrap)`

在该方法中执行 `fork` 操作，子进程用于业务处理，父进程返回子进程的 pid。

* 子进程的业务处理逻辑如下：
 1. 调用 `_child_process` 将该 service 封装在一个 Launch 中，并为其创建一个绿色线程。下面开始一个死循环：
 2. 调用 `_child_process_handle_signal` 再次为子进程绑定消息处理方法
 3. 调用 `_child_wait_for_exit_or_signal` 启动 launcher 。
 4. 调用 `_is_sighup_and_daemon` 处理发生的异常和捕获的信号



### `def _child_process(self, service)`

*该方法只会在子进程中调用*

1. 调用 `_child_process_handle_signal` 为子进程重新绑定信号处理方法
2. 调用 `os.close(self.writepipe)` 在子进程中关闭写管道（保证只有父进程对管道可写）
3. 孵化一个绿色线程，并调用 `_pipe_watcher` 方法，来检测父进程是否终止。
4. 创建一个 `Launcher` 实例。
5. 调用 `Launcher.launch_service` 方法

### `def _child_process_handle_signal(self)`

对于子进程，释放掉父进程绑定的信号处理方法，重新绑定新的信号处理方法。

```
    def _child_process_handle_signal(self):
        # Setup child signal handlers differently

        def _sigterm(*args):
            self.signal_handler.clear()
            self.launcher.stop()

        def _sighup(*args):
            self.signal_handler.clear()
            raise SignalExit(signal.SIGHUP)

        self.signal_handler.clear()

        # Parent signals with SIGTERM when it wants us to go away.
        self.signal_handler.add_handler('SIGTERM', _sigterm)
        self.signal_handler.add_handler('SIGHUP', _sighup)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)
```

### `def _pipe_watcher(self)`

采用阻塞的方式读管道，若是能在管道中读出数据的话，则意味着父进程已被杀死，此时子进程也应该退出。

```
    def _pipe_watcher(self):
        # This will block until the write end is closed when the parent
        # dies unexpectedly
        self.readpipe.read(1)

        LOG.info(_LI('Parent process has died unexpectedly, exiting'))

        if self.launcher:
            self.launcher.stop()

        sys.exit(1)
```

### `def _child_wait_for_exit_or_signal(self, launcher)`

在这里调用了 `launcher.wait` 来启动 service 

该方法会捕获所有的异常，并返回当前的状态和信号值

## `def _is_sighup_and_daemon(signo)`

对于 SIGHUP 方法，交由相应的处理方法进行处理

对于其他的则调用 `_is_daemon`

## `def _is_daemon()`

判断当前进程是否是守护进程

## `class Launcher(object)`

```
class Launcher(object):
    """Launch one or more services and wait for them to complete."""

    def __init__(self, conf, restart_method='reload'):
        """Initialize the service launcher.

        :param restart_method: If 'reload', calls reload_config_files on
            SIGHUP. If 'mutate', calls mutate_config_files on SIGHUP. Other
            values produce a ValueError.
        :returns: None

        """
        self.conf = conf
        conf.register_opts(_options.service_opts)
        self.services = Services()
        self.backdoor_port = (
            eventlet_backdoor.initialize_if_enabled(self.conf))
        self.restart_method = restart_method
        if restart_method not in _LAUNCHER_RESTART_METHODS:
            raise ValueError(_("Invalid restart_method: %s") % restart_method)
```

1. 创建一个 `Services` 实例
2. 调用 `eventlet_backdoor.initialize_if_enabled` 判断是否启动后门

### `def launch_service(self, service, workers=1)`



## `class Services(object)`

```
    def __init__(self):
        self.services = []
        self.tg = threadgroup.ThreadGroup()
        self.done = event.Event()
```

`ThreadGroup`  是对 `greenpool.GreenPool` 一个封装，默认绿色线程池的大小为10。

### `def add(self, service)`

```
    def add(self, service):
        """Add a service to a list and create a thread to run it.

        :param service: service to run
        """
        self.services.append(service)
        self.tg.add_thread(self.run_service, service, self.done)
```

孵化一个绿色线程，该线程内运行 `run_service` 方法

### `def run_service(service, done)`

```
    @staticmethod
    def run_service(service, done):
        """Service start wrapper.

        :param service: service to run
        :param done: event to wait on until a shutdown is triggered
        :returns: None

        """
        try:
            service.start()
        except Exception:
            LOG.exception(_LE('Error starting thread.'))
            raise SystemExit(1)
        else:
            done.wait()
```

调用一个 service 的 start 方法来启动该服务

### `def stop(self)`

1. 调用所有 service 的 stop 方法
2. 等待事件 event 是否结束，若未结束则调用 send 方法结束
3. 调用 `ThreadGroup.stop` 停止所有的绿色线程

### `def wait(self)`

```
    def wait(self):
        """Wait for services to shut down."""
        for service in self.services:
            service.wait()
        self.tg.wait()
```

1. 调用所有 servic 的 wait 方法
2. 调用所有绿色线程的 wait 方法

### `def restart(self)`

```
    def restart(self):
        """Reset services and start them in new threads."""
        self.stop()
        self.done = event.Event()
        for restart_service in self.services:
            restart_service.reset()
            self.tg.add_thread(self.run_service, restart_service, self.done)
```

将所有的 service 停止后重新启动

## `class ThreadGroup(object)`

*在 GreenPool 的基础上增加了 timer 的调用*

```
class ThreadGroup(object):
    """The point of the ThreadGroup class is to:

    * keep track of timers and greenthreads (making it easier to stop them
      when need be).
    * provide an easy API to add timers.
    """
    def __init__(self, thread_pool_size=10):
        self.pool = greenpool.GreenPool(thread_pool_size)
        self.threads = []
        self.timers = []
```

`threads` 用于记录孵化的绿色线程

### `def add_thread(self, callback, *args, **kwargs)`

```
    def add_thread(self, callback, *args, **kwargs):
        gt = self.pool.spawn(callback, *args, **kwargs)
        th = Thread(gt, self)
        self.threads.append(th)
        return th
```

孵化一个绿色线程，并以 `Thread` 进行封装。

### `def stop(self, graceful=False)`

```
    def stop(self, graceful=False):
        """stop function has the option of graceful=True/False.

        * In case of graceful=True, wait for all threads to be finished.
          Never kill threads.
        * In case of graceful=False, kill threads immediately.
        """
        self.stop_timers()
        if graceful:
            # In case of graceful=True, wait for all threads to be
            # finished, never kill threads
            self.wait()
        else:
            # In case of graceful=False(Default), kill threads
            # immediately
            self._stop_threads()
```

结束所有的 timer
结束所有的绿色线程

### `def _stop_threads(self)`

```
    def _stop_threads(self):
        self._perform_action_on_threads(
            lambda x: x.stop(),
            lambda x: LOG.exception(_LE('Error stopping thread.')))
```

### `def _perform_action_on_threads(self, action_func, on_error_func)`

```
    def _perform_action_on_threads(self, action_func, on_error_func):
        current = threading.current_thread()
        # Iterate over a copy of self.threads so thread_done doesn't
        # modify the list while we're iterating
        for x in self.threads[:]:
            if x.ident == current.ident:
                # Don't perform actions on the current thread.
                continue
            try:
                action_func(x)
            except eventlet.greenlet.GreenletExit:  # nosec
                # greenlet exited successfully
                pass
            except Exception:
                on_error_func(x)
```

结束所有其他的绿色线程

## `def wait(self)`

```
    def wait(self):
        for x in self.timers:
            try:
                x.wait()
            except eventlet.greenlet.GreenletExit:  # nosec
                # greenlet exited successfully
                pass
            except Exception:
                LOG.exception(_LE('Error waiting on timer.'))
        self._perform_action_on_threads(
            lambda x: x.wait(),
            lambda x: LOG.exception(_LE('Error waiting on thread.')))
```

等待所有的 timer 结束

等待所有的绿色线程结束

### `def stop_timers(self)`

```
    def stop_timers(self):
        for timer in self.timers:
            timer.stop()
        self.timers = []
```


## `class Thread(object)`

*对一个绿色线程的封装*

```
class Thread(object):
    """Wrapper around a greenthread.

     Holds a reference to the :class:`ThreadGroup`. The Thread will notify
     the :class:`ThreadGroup` when it has done so it can be removed from
     the threads list.
    """
    def __init__(self, thread, group):
        self.thread = thread
        self.thread.link(_on_thread_done, group, self)
        self._ident = id(thread)

    @property
    def ident(self):
        return self._ident

    def stop(self):
        self.thread.kill()

    def wait(self):
        return self.thread.wait()

    def link(self, func, *args, **kwargs):
        self.thread.link(func, *args, **kwargs)

    def cancel(self, *throw_args):
        self.thread.cancel(*throw_args)
```
