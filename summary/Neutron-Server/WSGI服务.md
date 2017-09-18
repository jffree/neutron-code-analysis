# Neutron-Server 中的 WSGI 服务

* 涉及到的 Python 模块：
 1. psste.deploy ： 用来加载 wsgi app
 2. eventlet ： 用来启动  wsgi server

## neutron-server 的启动

```
/usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini & echo $! >/opt/stack/status/stack/q-svc.pid; fg || echo "q-svc failed to start" | tee "/opt/stack/status/stack/q-svc.failure"
```

有耐心的可以跟着代码从开始向后追踪，我这里只列出重点。

## WSGI APP 的加载

在 *neutron/service.py* 中：

```
def _run_wsgi(app_name):
    app = config.load_paste_app(app_name)
    if not app:
        LOG.error(_LE('No known API applications configured.'))
        return
    return run_wsgi_app(app)
```

这个方法实现了 WSGI APP 的加载，如果你继续向下追踪的话，可以看到最终是调用了 `paste.deploy` 模块。

相关文件：*api-paste.ini*

## WSGI Server 的创建

* 在 *neutron/wsgi.py* 的 `class Server(object)` 类中：
 1. `def _get_socket(self, host, port, backlog)` 方法，用于创建 WSGI Server 的 socket
 2. `def _run(self, application, socket)` 调用 `eventlet.wsgi` 来启动 WSGI Server

## 其他

* 一个 WSGI Server 会涉及到很多方面，包括：
 1. 配置信息的加载
 2. log 的设定
 3. 多进程的启动
 4. 信号的处理
 5. 进程间的通讯

这些都是要考虑的部分，有兴趣的可以深入阅读一下。

## 参考

[ 详解Paste deploy ](http://www.cnblogs.com/Security-Darren/p/4087587.html)