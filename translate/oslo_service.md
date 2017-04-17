# oslo_service

oslo.service提供了一个框架，用于使用其他OpenStack应用建立的模式来定义新的长时间运行的服务。它还包括长期运行的应用程序可能需要的 SSL 或 WSGI，执行周期性操作，与systemd进行交互等特性。

## 安装

```
$ pip install oslo.service
```

## 使用

在项目中使用 oslo.service：

```
import oslo_service
```

### 迁移到 oslo.service

oslo.service 库不再假定全局配置对象可用。相反，以下函数和类已更改，以期望应用传入一个 oslo.config 的配置对象：

* `initialize_if_enabled()`

* `oslo_service.periodic_task.PeriodicTasks`

* `launch()`

* `oslo_service.service.ProcessLauncher`

* `oslo_service.service.ServiceLauncher`

* `is_enabled()`

* `wrap()`

### When using service from oslo-incubator

```
from foo.openstack.common import service

launcher = service.launch(service, workers=2)
```

### When using oslo.service

```
from oslo_config import cfg
from oslo_service import service

CONF = cfg.CONF
launcher = service.launch(CONF, service, workers=2)
```

### Using oslo.service with oslo-config-generator

oslo.service 提供了几个入口点来生成配置文件。

* `oslo.service.service`

 * 来自 service 以及来自 eventlet_backdoor 模块为 [DEFAULT] 段的选项。

* `oslo.service.periodic_task`

 * 来自 periodic_task 模块为 [DEFAULT] 段的选项。

* `oslo.service.sslutils`

 * 来自 sslutils  模块为 [ssl] 段的选项。

* `oslo.service.wsgi`

 * 来自 wsgi 模块为 [DEFAULT] 段的选项。

**注意：**该库不提供 oslo.service 入口点。

```
$ oslo-config-generator --namespace oslo.service.service \
--namespace oslo.service.periodic_task \
--namespace oslo.service.sslutils
```

### 启动并控制服务

oslo_service.service 模块提供了启动 OpenStack 服务并控制其生命周期的工具。

一个服务可以是 `oslo_service.service.ServiceBase` 任何子类的一个实例。 ServiceBase 是一个抽象类，定义每个服务应实现的接口。 oslo_service.service.Service 可以作为构建新服务的基础。

#### 启动

oslo_service.service 模块提供两个运行服务的启动器：

* `oslo_service.service.ServiceLauncher` - 用于在父进程中运行一个或多个服务。

* `oslo_service.service.ProcessLauncher` - 分配一定数量的 workers，然后启动服务。

可以初始化所需的启动器，然后使用它启动服务。

```
from oslo_config import cfg
from oslo_service import service

CONF = cfg.CONF


service_launcher = service.ServiceLauncher(CONF)
service_launcher.launch_service(service.Service())

process_launcher = service.ProcessLauncher(CONF, wait_interval=1.0)
process_launcher.launch_service(service.Service(), workers=2)
```

或者可以简单地调用 `oslo_service.service.launch()`，它将根据传递给它的 worker 的数量自动选择适当的启动器（如果worker = 1，则为ServiceLauncher或在其他情况下为 None 或 ProcessLauncher ）。

```
from oslo_config import cfg
from oslo_service import service

CONF = cfg.CONF

launcher = service.launch(CONF, service.Service(), workers=3)
```

**请注意**，强烈建议每个进程使用不超过一个 ServiceLauncher 和 ProcessLauncher 类的实例。

#### 信号处理

`oslo_service.service` 为 SIGTERM，SIGINT 和 SIGHUP 等信号提供处理程序。

SIGTERM 用于优雅地终止服务。这可以允许服务器等待所有客户端关闭连接，同时拒绝新的传入请求。 配置选项 `graceful_shutdown_timeout` 指定在接收到SIGTERM信号后多少秒，服务器应继续运行，处理现有连接。将 graceful_shutdown_timeout 设置为零表示服务器将无限期地等待，直到所有剩余的请求服务都已完全提供。

要强制立即终止 需要发送 SIGINT 信号。

一旦接收大 SIGHUP 信号，配置文件将被重新加载并且服务将被重置并重新启动。 然后使用SIGTERM 正常地停止 child workers 的工作，并且根据新配置产生新的 workers。 因此，SIGHUP 可用于随时随地更改配置选项。

注意：Windows不支持SIGHUP。
注意：Windows上不支持配置选项 graceful_shutdown_timeout。

以下是具有重置方法的服务的示例，该方法允许通过发送SIGHUP来重新加载日志记录选项。

```
from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

class FooService(service.ServiceBase):

    def start(self):
        pass

    def wait(self):
        pass

    def stop(self):
        pass

    def reset(self):
        logging.setup(cfg.CONF, 'foo')
```

## 配置选项

oslo.service 使用 oslo.config 来定义和管理配置选项，以允许部署者控制应用程序如何使用此库。

### periodic_task

这些选项适用于使用 oslo.service 的定期任务功能的服务。

#### DEFAULT

```
run_external_periodic_tasks
   Type:	boolean
   Default:	true
```

一些周期性的任务可以在一个单独的进程中运行。我们应该在这里运行他们吗？

### service

这些选项适用于使用基本服务框架的服务。

```
backdoor_port
    Type:	string
    Default:	<None>
```

启用 eventlet 后门。可接受的值为 `0，<port>和<start>：<end>`。其中 0 意味着侦听随机 tcp 端口号; <port> 侦听指定的端口号（如果该端口正在使用，则不启用后门）; 而 <start>：<end> 则是指定监听端口号的范围并选择最小未使用的端口号。所选端口显示在服务的日志文件中。

```
backdoor_socket
    Type:	string
    Default:	<None>
```

启用 eventlet 后门，使用提供的路径作为可以接收连接的unix套接字。 此选项与 `backdoor_port` 互斥，因为只应提供一个。如果同时提供这两个选项，则该选项的存在将覆盖那个选项的用法。

```
log_options
    Type:	boolean
    Default:	true
```

启动或禁用启动服务时所有注册选项的日志记录值（DEBUG级别）。

```
graceful_shutdown_timeout
    Type:	integer
    Default:	60
```

指定一个超时时间，正常关闭服务并退出。0 意味着无止境的等待。

### sslutils

这些选项适用于使用SSL的服务。

#### ssl

```
ca_file
    Type:	string
    Default:	<None>
```

用于验证连接客户端的CA证书文件。

已弃用的值：

```
Group	Name
DEFAULT	ssl_ca_file
```

```
cert_file
    Type:	string
    Default:	<None>
```

安全启动服务器时使用的证书文件。


已弃用的值：

```
Group	Name
DEFAULT	ssl_cert_file
```

```
key_file
   Type:	string
   Default:	<None>
```

安全启动服务器时使用的私钥文件。

已弃用的值

```
Group	Name
DEFAULT	ssl_key_file
```

```
version
    Type:	string
    Default:	<None>
```

使用SSL版本（仅在启用SSL时有效）。有效值为TLSv1和SSLv23。某些发行版可能会提供SSLv2，SSLv3，TLSv1_1和TLSv1_2。

```
ciphers
    Type:	string
    Default:	<None>
```

设置可用密码的列表。值应该是OpenSSL密码列表格式的字符串。

### wsgi

这些选项适用于使用WSGI（Web服务网关接口）模块的服务。

#### DEFAULT

```
api_paste_config
    Type:	string
    Default:	api-paste.ini
```

api服务的 `paste.deploy` 配置文件名

```
wsgi_log_format
    Type:	string
    Default:	%(client_ip)s "%(request_line)s" status: %(status_code)s  len: %(body_length)s time: %(wall_seconds).7f
````

用作生成日志行的模板的python格式字符串。可以将以下值格式化为：client_ip，date_time，request_line，status_code，body_length，wall_seconds。

```
tcp_keepidle
    Type:	integer
    Default:	600
```

为每个服务套接字设置 TCP_KEEPIDLE 的值（以秒为单位）。 OS X不支持

```
wsgi_default_pool_size
    Type:	integer
    Default:	100
```

wsgi使用的greenthreads池的大小

```
max_header_line
    Type:	integer
    Default:	16384
```

要接受的信息标题的最大行大小。当使用大的令牌（通常是将keystone配置为使用具有大型服务目录的PKI令牌时生成的令牌），max_header_line可能需要增加。

```
wsgi_keep_alive
    Type:	boolean
    Default:	true
```

如果为False，则显式关闭客户端套接字连接。

```
client_socket_timeout
    Type:	integer
    Default:	900
```

客户端连接的套接字操作的允许超时时间。如果超过这个秒数，它将被关闭。值“0”表示永远等待。

## [API Documentation](https://docs.openstack.org/developer/oslo.service/index.html#api-documentation)