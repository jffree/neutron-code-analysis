# neutron server 的启动过程

## neutron-server 的 entry point

我们首先看 neutron 源码中的 setup.cfg 文件：

```
[entry_points]
console_scripts =
...
    neutron-server = neutron.cmd.eventlet.server:main
```

然后我们找到 *neutron/cmd/eventlet/server/__init__.py* 中的 `main` 方法：

```
def main():
    server.boot_server(_main_neutron_server)
```

`boot_server` 方法的实现在 *neutron/server/__init__.py*

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

`_main_neutron_server` 方法依然是在 *neutron/cmd/eventlet/server/__init__.py* 实现的：

```
def _main_neutron_server():
    if cfg.CONF.web_framework == 'legacy':
        wsgi_eventlet.eventlet_wsgi_server()
    else:
        wsgi_pecan.pecan_wsgi_server()
```

`_main_neutron_server` 是根据配置中 wsgi 框架的不同来选择不同的启动方法， neutron 中默认是以 `legacy` 的方式启动 wsgi 服务的，我们就按照这个来分析。


`eventlet_wsgi_server` 方法是在 *neutron/server/wsgi_eventlet.py* 中实现的：

```
def eventlet_wsgi_server():
    neutron_api = service.serve_wsgi(service.NeutronApiService)
    start_api_and_rpc_workers(neutron_api)
```

这个方法做了两个工作：

1. 启动 neutron 中的 wsgi 服务

2. 启动 neutron 中的 rpc 服务

### neutron 中的 wsgi 服务

我先先来看 `service.serve_wsgi` 这个方法（*neutron/service.py*）

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

















