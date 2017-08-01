# Neutron Agent AsyncProcess

*neutron/agent/linux/async_process.py*

## `class AsyncProcess(object)`

* 描述：
 1. 该类可以根据命令启动一个子进程来执行该命令
 2. 运行该子进程后还可以读取 stdout 和 stderr 的输出
 3. 若是 `respawn_interval` 参数不为0，则子进程有错误产生时会重启子进程

```
    def __init__(self, cmd, run_as_root=False, respawn_interval=None,
                 namespace=None, log_output=False, die_on_error=False):
        """Constructor.

        :param cmd: The list of command arguments to invoke.
        :param run_as_root: The process should run with elevated privileges.
        :param respawn_interval: Optional, the interval in seconds to wait
               to respawn after unexpected process death. Respawn will
               only be attempted if a value of 0 or greater is provided.
        :param namespace: Optional, start the command in the specified
               namespace.
        :param log_output: Optional, also log received output.
        :param die_on_error: Optional, kills the process on stderr output.
        """
        self.cmd_without_namespace = cmd
        self._cmd = ip_lib.add_namespace_to_cmd(cmd, namespace)
        self.run_as_root = run_as_root
        if respawn_interval is not None and respawn_interval < 0:
            raise ValueError(_('respawn_interval must be >= 0 if provided.'))
        self.respawn_interval = respawn_interval
        self._process = None
        self._is_running = False
        self._kill_event = None
        self._reset_queues()
        self._watchers = []
        self.log_output = log_output
        self.die_on_error = die_on_error
```

### `def _reset_queues(self)`

构造两个队列，分别用来读取标准输出和标准错误输出

```
    def _reset_queues(self):
        self._stdout_lines = eventlet.queue.LightQueue()
        self._stderr_lines = eventlet.queue.LightQueue()
```

### `def start(self, block=False)`

调用 `_spawn` 启动子进程

### `def _spawn(self)`

1. 为命令 cmd 启动子进程
2. 启动两个线程，分别运行 `_read_stdout` 和 `_read_stderr` 来循环读取程序的输出

### `def _read_stdout(self)`

将程序的标准输出读取到 `_stdout_lines` 队列中

### `def _read_stderr(self)`

将程序的标准错误读取到 `_stderr_lines` 队列中

### `def iter_stdout(self, block=False)`

通过读取 `_stdout_lines` 读取程序的标准输出

### `def iter_stderr(self, block=False)`

通过读取 `_stderr_lines` 读取程序的标准错误输出

### `def _handle_process_error(self)`

子进程运行出现问题时，调用 `_kill` 将其杀掉。若设置了 `respawn_interval`，则会再次将其重启。

### `def pid(self)`

cmd 运行时的 pid

### `def _kill(self, kill_signal)`

杀掉子进程，并杀掉读取 stdout 和 stderr 的线程

### `def stop(self, block=False, kill_signal=signal.SIGKILL)`

停止子进程。调用 `_kill` 实现

### `def is_active(self)`

查询子进程是否是 active。