# Neutron WSGI/HTTP API layer

本节将介绍Neutron的HTTP API的内部结构以及Neutron中可用于为Neutron API创建Extensions的类。

Python Web应用程序通过Python Web服务器网关接口（WSGI）与Web服务器进行通信。 - 在[PEP 333](http://legacy.python.org/dev/peps/pep-0333/)中定义

## 开始

Neutron的WSGI服务器从 [server module](http://git.openstack.org/cgit/openstack/neutron/tree/neutron/server/__init__.py) 启动，并且调用 entry point `serve_wsgi` 来构建 [NeutronApiService](http://git.openstack.org/cgit/openstack/neutron/tree/neutron/service.py) 的实例，然后将其返回给 server module，该 server module 生成将运行WSGI应用程序并响应客户端请求的 [Eventlet](http://eventlet.net/) [GreenPool](http://eventlet.net/doc/modules/greenpool.html)。

## WSGI 应用

在构建 `NeutronApiService` 期间，`_run_wsgi` 函数使用 [config.py](http://git.openstack.org/cgit/openstack/neutron/tree/neutron/common/config.py) 中的 `load_paste_app` 函数创建一个WSGI应用程序，该函数解析 [api-paste.ini](http://git.openstack.org/cgit/openstack/neutron/tree/etc/api-paste.ini)，以便使用 [Paste](http://pythonpaste.org/) 的 [deploy](http://pythonpaste.org/deploy/) 来创建一个WSGI应用程序。

api-paste.ini文件使用[Paste INI 文件格式](http://pythonpaste.org/deploy/#applications)定义WSGI应用程序和路由。

INI文件指示 paste 实例化 Neutron 的 [APIRouter](http://git.openstack.org/cgit/openstack/neutron/tree/neutron/api/v2/router.py) 类，其中包含将Neutron资源（如端口，网络，子网）映射到URL的几种方法，以及每个资源的控制器。

## 进一步阅读

[Yong Sheng Gong: Deep Dive into Neutron](http://www.slideshare.net/gongys2004/inside-neutron-2)