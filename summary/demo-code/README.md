# 简介

当前目录下是一些功能的小的 demo

## wsgi and rpc

* 模仿 neutron-server 写了一个小 demo，功能如下：
 1. 主进程下启动了两个子进程，这两个子进程分别负责启动 wsgi server 服务和 rpc server 服务
 2. 主进程调用 oslo_server.ProcessLauncher 来启动子进程
 3. wsgi 服务中使用 paste.deploy 来加载 wsgi app
 4. wsgi 服务中使用 eventlet.wsgi 来启动 wsgi server
 5. wsgi 服务中使用 routes 来对请求路径进行解析和分发
 6. 通过调用 oslo_messaging 来启动 rpc server
 7. rpc_client.py 是 rpc 客户端的测试代码

* 启动

```
python service.py
```



