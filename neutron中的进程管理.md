# oslo\_service 中的程管理的框架

`oslo_service` 包完成了后台服务的管理。我们这里只说进程管理的部分，这些全部在 _oslo\_service/service.py_ 中实现。

## 服务的封装类

* `class ServiceBase` 是服务的抽象类，它定义了服务至少需要实现的方法： `start`、`stop`、`wait`、`rest`。具体的服务为 `ServiceBase` 子类的实例。

* `class ServiceWrapper` 封装了具体服务的一些属性  
  1. `service` 具体服务的实例  
  2. `workers` 服务的进程数  
  3. `children` 保存服务所以进程的 pid  
  4. `forktimes` 每个进程 fork 的时间

## 服务的管理类

### `class Services` 这个类是所有的 service 实例的管理类

* `__init__`

  1. `services` 保存所有的具体服务的实例
  2. `tg` 绿色线程池的封装（`threadgroup.ThreadGroup`）实例
  3. `done` eventlet的事件对象

* `add` 增加一个服务实例，并为它启动一个绿色线程（**这是服务的真正启动点**）

* `stop` 调用所有服务实例的 `stop` 方法，并结束所有的绿色线程

* `wait` 调用所有服务实例的 `wait` 方法

* `restart` 重置所有服务实例，并以新的绿色线程启动它

* `run_service` 启动所有服务实例（调用服务实例的 `start` 方法）

### `class Launcher`

`class Services` 的封装类，做一些辅助动作，例如：

1. 为每个服务实例设定一个 `backdoor_port` 属性  **？？**

2. 根据 `restart_method` 方法的不同重新导入不同的配置文件

## 服务的进程管理类

### `class ServiceLauncher`

* `ServiceLauncher` 是在当前的进程下启动服务，而不再为服务启动（`fork`）新的进程。

* `ServiceLauncher` 还对综合了信号处理（`SignalHandler`）的功能

```
    def handle_signal(self):
        """Set self._handle_signal as a signal handler."""
        self.signal_handler.clear()
        self.signal_handler.add_handler('SIGTERM', self._graceful_shutdown)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)
        self.signal_handler.add_handler('SIGHUP', self._reload_service)
        self.signal_handler.add_handler('SIGALRM', self._on_timeout_exit)
```

### `class ProcessLauncher`

* 当一个服务需要在多个进程中启动时，你需要用到 `ProcessLauncher` 来实现

* `ProcessLauncher` 会根据服务要求的进程数（`workers`），来启动（`fork`）多个进程

* 在每个进程中，`ProcessLauncher` 会启动一个 `Launcher` 来管理服务实例

* `ProcessLauncher` 同样具有信号管理能力（`SignalHandler`）

## 信号管理类

* `class SignalHandler`

* `class SignalExit`

# neutron 中的进程管理

* 在 _neutron/worker.py_ 中定义了一个继承于 oslo\_service 中的 `ServiceBase` 类的抽象子类 `NeutronWorker`

## neutron 中 wsgi 服务的进程管理

* 在 _neutron/wsgi.py_ 中定义了一个继承于 `NeutronWorker` 的子类 `WorkerService`，该子类实现了 wsgi 服务的 `start`、`wait`、`stop`、`reset` 方法；

* 若希望在多个进

* 程（`worker_process_count`）中启动 wsgi 服务，则会用 oslo\_service 的 `ProcessLauncher` 来进行进程的启动和管理，然后在进程中启动 wsgi 服务；

* 若希望在当前的进程中启动 wsgi 服务，则会直接运行 `WorkerService` 的 `start` 方法

## neutron 中 rpc 服务的进程管理

* 在 rpc 服务中有四种 worker，这三种都是对 `NeutronWorker` 的继承

  1. `RpcWorker` 负责启动所有插件（核心和服务）的 rpc 服务；
  2. `RpcReportsWorker` 继承于 `RpcWorker` 负责监听 rpc 状态
  3. `AgentStatusCheckWorker`，监视 agent 状态
  4. `AllServicesNeutronWorker` 对于有的插件不想为 rpc 服务启动多进程，只在当前进程中启动就可以，那么 neutron 会将这些插件集合起来，在一个单独的进程中启动

* 为 rpc 服务启动进程时，会先收集需要启动的 worker：
 1. 为所有的 plugin （包括核心和服务插件）准备 worker（`RpcWorker`），进程个数为配置文件中的`rpc_workers` 
 2. 若配置文件中有 `rpc_state_report_workers` 这个选项，且插件支持 report ，则准备 report woker （`RpcReportsWorker`），个数为 `rpc_state_report_workers`
 3. 每个插件都有 `get_workers` 方法，若某个插件需要单独的为某个动作启动一个进程时则会实现这个方法，返回 woker 的列表。（上面说到的 `AgentStatusCheckWorker` 就是在这里返回的。）
 4. 通过前三步收集起来的所有 worker 里面，若有的 worker 不希望单独启动一个进程，则将这些 worker 整合到一个单独的进程 `AllServicesNeutronWorker` 中。

* 当有的插件希望为 rpc 服务启动多个进程有的插件不希望为 rpc 服务启动多进程时：  
  1. 用 `ProcessLauncher` 管理希望启动多进程的插件的 rpc 服务  
  2. 将所有不想启动多进程的插件集合到一个 worker 中，也用 `ProcessLauncher` 为其启动单独一个进程

* 当所有的插件都不想为 rpc 服务启动多进程时，那么就会利用 `ServiceLauncher` 在当前的进程中来为每个插件启动 rpc 服务。

# neutron-service 进程实例：

```
[root@localhost oslo_service]# ps -aux | grep neutron-server
stack     54006 11.8  0.5 290780 91844 pts/10   S+   12:39   0:07 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54022  0.0  0.5 290780 87208 pts/10   S+   12:39   0:00 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54023  0.0  0.5 290780 87204 pts/10   S+   12:39   0:00 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54024  0.0  0.5 290780 87204 pts/10   S+   12:39   0:00 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54025  0.0  0.5 290780 87204 pts/10   S+   12:39   0:00 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54026  5.7  0.6 301832 98880 pts/10   S+   12:39   0:03 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54027  0.7  0.5 294044 91072 pts/10   S+   12:39   0:00 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
stack     54028  0.7  0.5 295364 92312 pts/10   S+   12:39   0:00 /usr/bin/python /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
root      54151  0.0  0.0 112648   960 pts/32   S+   12:40   0:00 grep --color=auto neutron-server
```

* rpc 所有的 woker 为

```
[<neutron.service.RpcWorker object at 0x4b16c10>, <neutron.service.RpcReportsWorker object at 0x4b16c90>, <neutron.db.agentschedulers_db.AgentStatusCheckWorker object at 0x4ffe410>, <neutron.db.agentschedulers_db.AgentStatusCheckWorker object at 0x4ffe6d0>, <neutron.service.RpcWorker object at 0x5018f50>]
```

* 进程分析：
 1. 主进程为 54006
 2. 配置文件中 `api_workers = 4` 意味着 wsgi 服务的进程数为为 4（54022、54023、54024、54025）
 3. 配置文件中 `rpc_workers=1` 意味着为所有的插件启动一个单独的进程（54026）
 4. 配置文件中 `rpc_state_report_workers=1` 意味着为 rpc state report启动一个单独的进程（54027）
 5. 通过插件的 `get_workers`方法获取了三个 worker，这三个 worker 都不要求启动队里进程，所有通过一个 `AllServicesNeutronWorker` 进程来启动他们（54028）