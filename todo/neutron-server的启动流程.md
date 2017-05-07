# neutron server 的启动过程

## neutron-server 的 entry point

我们首先看 neutron 源码中的 setup.cfg 文件：

```
[entry_points]
console_scripts =
...
    neutron-server = neutron.cmd.eventlet.server:main
```

然后我们找到 _neutron/cmd/eventlet/server/**init**.py_ 中的 `main` 方法：

```
def main():
    server.boot_server(_main_neutron_server)
```

`boot_server` 方法的实现在 _neutron/server/**init**.py_

```
def boot_server(server_func):
    # the configuration will be read into the cfg.CONF global data structure
    config.init(sys.argv[1:])
    config.setup_logging()
    config.set_config_defaults()
    if not cfg.CONF.config_file:
        sys.exit(_("ERROR: Unable to find configuration file via the default"
                   " search paths (~/.neutron/, ~/, /etc/neutron/, /etc/) and"
                   " the '--config-file' option!"))
    try:
        server_func()
    except KeyboardInterrupt:
        pass
    except RuntimeError as e:
        sys.exit(_("ERROR: %s") % e)
```

`boot_server` 做了如下几个工作

1. 读入命令行参数
2. 设定 log 配置
3. 设置 neutron 的默认配置
4. 运行启动 neutron-server 的方法

`_main_neutron_server` 方法依然是在 _neutron/cmd/eventlet/server/**init**.py_ 实现的：

```
def _main_neutron_server():
    if cfg.CONF.web_framework == 'legacy':
        wsgi_eventlet.eventlet_wsgi_server()
    else:
        wsgi_pecan.pecan_wsgi_server()
```

`_main_neutron_server` 是根据配置中 wsgi 框架的不同来选择不同的启动方法， neutron 中默认是以 `legacy` 的方式启动 wsgi 服务的，我们就按照这个来分析。

`eventlet_wsgi_server` 方法是在 _neutron/server/wsgi\_eventlet.py_ 中实现的：

```
def eventlet_wsgi_server():
    neutron_api = service.serve_wsgi(service.NeutronApiService)
    start_api_and_rpc_workers(neutron_api)
```

这个方法做了两个工作：

1. 启动 neutron 中的 wsgi 服务

2. 启动 neutron 中的 rpc 服务

### neutron 中的 wsgi 服务

我先先来看 `service.serve_wsgi` 这个方法（_neutron/service.py_）

```
def serve_wsgi(cls):

    try:
        service = cls.create()
        service.start()
    except Exception:
        with excutils.save_and_reraise_exception():
            LOG.exception(_LE('Unrecoverable error: please check log '
                              'for details.'))

    registry.notify(resources.PROCESS, events.BEFORE_SPAWN, service)
    return service
```

这个方法做了三件事情：

1. 实例化一个类（service.NeutronApiService）

2. 调用了这个类的 `start` 方法

3. 将这个类的实例注册到回调系统中（这个我们以后再解析）。

那么下面我们就仔细看看 `service.NeutronApiService` 这个类（_neutron/service.py_）：

```
class WsgiService(object):
    """Base class for WSGI based services.

    For each api you define, you must also define these flags:
    :<api>_listen: The address on which to listen
    :<api>_listen_port: The port on which to listen

    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.wsgi_app = None

    def start(self):
        self.wsgi_app = _run_wsgi(self.app_name)

    def wait(self):
        self.wsgi_app.wait()


class NeutronApiService(WsgiService):
    """Class for neutron-api service."""
    def __init__(self, app_name):
        profiler.setup('neutron-server', cfg.CONF.host)
        super(NeutronApiService, self).__init__(app_name)

    @classmethod
    def create(cls, app_name='neutron'):
        # Setup logging early
        config.setup_logging()
        service = cls(app_name)
        return service
```

`NeutronApiService` 在实例化时，为 osprofiler（openstack 性能调优工具）做了初始化的配置。

那么主要的就在 `start` 方法里面了，`start` 方法只是调用了 `_run_wsgi` 方法（也是在 _neutron/service.py_ 中）：

```
def _run_wsgi(app_name):
    app = config.load_paste_app(app_name)
    if not app:
        LOG.error(_LE('No known API applications configured.'))
        return
    return run_wsgi_app(app)
```

在这里面，`_run_wsgi` 方法做了两件事情：

1. 加载 `neutron` app
2. 启动 `neutron` app

#### neutron app 的加载

`load_paste_app` 方法在 _neutron/common/config.py_ 中定义：

```
def load_paste_app(app_name):
    """Builds and returns a WSGI app from a paste config file.

    :param app_name: Name of the application to load
    """
    loader = wsgi.Loader(cfg.CONF)
    app = loader.load_app(app_name)
    return app
```

`Loader` 是 `oslo_service` 包中的一个类，是对于 `paste` 包的一层封装。

1. `Loader.__init__` 方法实现查找用于 `paste` 包的配置文件的位置；
2. `Loader.load_app` 通过调用 `paste.deploy.loadapp` 来加载 `neutron` app；

#### neutron app 的启动

`run_wsgi_app` 在 _neutron/service.py_ 中定义：

```
def run_wsgi_app(app):
    server = wsgi.Server("Neutron")
    server.start(app, cfg.CONF.bind_port, cfg.CONF.bind_host,
                 workers=_get_api_workers())
    LOG.info(_LI("Neutron service started, listening on %(host)s:%(port)s"),
             {'host': cfg.CONF.bind_host, 'port': cfg.CONF.bind_port})
    return server

...

def _get_api_workers():
    workers = cfg.CONF.api_workers
    if workers is None:
        workers = processutils.get_worker_count()
    return workers
```

参数介绍：

1. bind\_port 建立监听的端口
2. bind\_host 建立监听的主机
3. api\_workers 指定进程的数量，若不指定则默认为 cpu 的个数

##### 服务的封装 `Server` （wsgi socket and app 的大管家 `Server`）

`Server` 是在 _neutron/wsgi.py_ 中实现的：

```
class Server(object):
    """Server class to manage multiple WSGI sockets and applications."""

    def __init__(self, name, num_threads=None, disable_ssl=False):
        # Raise the default from 8192 to accommodate large tokens
        eventlet.wsgi.MAX_HEADER_LINE = CONF.max_header_line
        self.num_threads = num_threads or CONF.wsgi_default_pool_size
        self.disable_ssl = disable_ssl
        # Pool for a greenthread in which wsgi server will be running
        self.pool = eventlet.GreenPool(1)
        self.name = name
        self._server = None
        # A value of 0 is converted to None because None is what causes the
        # wsgi server to wait forever.
        self.client_socket_timeout = CONF.client_socket_timeout or None
        if CONF.use_ssl and not self.disable_ssl:
            sslutils.is_enabled(CONF)

    def _get_socket(self, host, port, backlog):
        bind_addr = (host, port)
        # TODO(dims): eventlet's green dns/socket module does not actually
        # support IPv6 in getaddrinfo(). We need to get around this in the
        # future or monitor upstream for a fix
        try:
            info = socket.getaddrinfo(bind_addr[0],
                                      bind_addr[1],
                                      socket.AF_UNSPEC,
                                      socket.SOCK_STREAM)[0]
            family = info[0]
            bind_addr = info[-1]
        except Exception:
            LOG.exception(_LE("Unable to listen on %(host)s:%(port)s"),
                          {'host': host, 'port': port})
            sys.exit(1)

        sock = None
        retry_until = time.time() + CONF.retry_until_window
        while not sock and time.time() < retry_until:
            try:
                sock = eventlet.listen(bind_addr,
                                       backlog=backlog,
                                       family=family)
            except socket.error as err:
                with excutils.save_and_reraise_exception() as ctxt:
                    if err.errno == errno.EADDRINUSE:
                        ctxt.reraise = False
                        eventlet.sleep(0.1)
        if not sock:
            raise RuntimeError(_("Could not bind to %(host)s:%(port)s "
                               "after trying for %(time)d seconds") %
                               {'host': host,
                                'port': port,
                                'time': CONF.retry_until_window})
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sockets can hang around forever without keepalive
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # This option isn't available in the OS X version of eventlet
        if hasattr(socket, 'TCP_KEEPIDLE'):
            sock.setsockopt(socket.IPPROTO_TCP,
                            socket.TCP_KEEPIDLE,
                            CONF.tcp_keepidle)

        return sock

    def start(self, application, port, host='0.0.0.0', workers=0):
        """Run a WSGI server with the given application."""
        self._host = host
        self._port = port
        backlog = CONF.backlog

        self._socket = self._get_socket(self._host,
                                        self._port,
                                        backlog=backlog)

        self._launch(application, workers)

    def _launch(self, application, workers=0):
        service = WorkerService(self, application, self.disable_ssl, workers)
        if workers < 1:
            # The API service should run in the current process.
            self._server = service
            # Dump the initial option values
            cfg.CONF.log_opt_values(LOG, logging.DEBUG)
            service.start()
            systemd.notify_once()
        else:
            # dispose the whole pool before os.fork, otherwise there will
            # be shared DB connections in child processes which may cause
            # DB errors.
            api.context_manager.dispose_pool()
            # The API service runs in a number of child processes.
            # Minimize the cost of checking for child exit by extending the
            # wait interval past the default of 0.01s.
            self._server = common_service.ProcessLauncher(cfg.CONF,
                                                          wait_interval=1.0)
            self._server.launch_service(service,
                                        workers=service.worker_process_count)

    @property
    def host(self):
        return self._socket.getsockname()[0] if self._socket else self._host

    @property
    def port(self):
        return self._socket.getsockname()[1] if self._socket else self._port

    def stop(self):
        self._server.stop()

    def wait(self):
        """Wait until all servers have completed running."""
        try:
            self._server.wait()
        except KeyboardInterrupt:
            pass

    def _run(self, application, socket):
        """Start a WSGI server in a new green thread."""
        eventlet.wsgi.server(socket, application,
                             max_size=self.num_threads,
                             log=LOG,
                             keepalive=CONF.wsgi_keep_alive,
                             socket_timeout=self.client_socket_timeout)
```

* `__init__` 方法根据配置定义了一些默认的属性，这些定义都可以参考 _neutron.conf_   
  1.  `max_header_line` 消息体 header 中的最大 line number  
  2.  `num_threads(wsgi_default_pool_size)` 绿色线程池的大小  
  3.  `disable_ssl` 是否启用 ssl  
  4.  `poll` 启动一个绿色线程池  
  5.  `name` `Server` 的名称  
  6.  `client_socket_timeout` socket 连接的超时时间

* `_get_socket` 方法用来建立一个 socket 的监听   
  1. `backolog` 用来是关于TCP连接的大小：![TCP 为套接字维护的两个对立](http://pic002.cnblogs.com/images/2012/107596/2012070820074666.png)  
  2.  `retry_until_window` 尝试去建立监听的时间（秒）  
  3.  `tcp_keepidle` 对一个连接进行有效性探测之前运行的最大非活跃时间间隔（参考：[TCP 连接断连问题剖析](https://www.ibm.com/developerworks/cn/aix/library/0808_zhengyong_tcp/)）；  
  4.  这个方法调用了 `eventlet.listen` 建立 socket 监听

* `start` 获取 socket 后调用了 `_launch` 方法

##### 进程的封装 `WorkerService`

`WorkerService` 也是在 _neutron/wsgi.py_ 中实现的：

```
class WorkerService(neutron_worker.NeutronWorker):
    """Wraps a worker to be handled by ProcessLauncher"""
    def __init__(self, service, application, disable_ssl=False,
                 worker_process_count=0):
        super(WorkerService, self).__init__(worker_process_count)

        self._service = service
        self._application = application
        self._disable_ssl = disable_ssl
        self._server = None

    def start(self):
        super(WorkerService, self).start()
        # When api worker is stopped it kills the eventlet wsgi server which
        # internally closes the wsgi server socket object. This server socket
        # object becomes not usable which leads to "Bad file descriptor"
        # errors on service restart.
        # Duplicate a socket object to keep a file descriptor usable.
        dup_sock = self._service._socket.dup()
        if CONF.use_ssl and not self._disable_ssl:
            dup_sock = sslutils.wrap(CONF, dup_sock)
        self._server = self._service.pool.spawn(self._service._run,
                                                self._application,
                                                dup_sock)

    def wait(self):
        if isinstance(self._server, eventlet.greenthread.GreenThread):
            self._server.wait()

    def stop(self):
        if isinstance(self._server, eventlet.greenthread.GreenThread):
            self._server.kill()
            self._server = None

    @staticmethod
    def reset():
        config.reset_service()
```



