# extension 调试过程：

## wsgi 框架

* `api-paste.ini` 找到 `extensions filter`

* `neutron.api.extension` 找到 `plugin_aware_extension_middleware_factory`。（根据 paste.deploy 的使用， filter 是接受一个 aap 为参数再返回一个 app。）

## 构造路由映射，分发路由请求

* 通过 `plugin_aware_extension_middleware_factory` 找到 `ExtensionMiddleware`，这个 filter 返回的就是 `ExtensionMiddleware` 实例为 app。

* 在 `ExtensionMiddleware` 的 `__init__` 方法中利用 `routes.Mapper` 实现了 extension 路由映射， `mapper` 变量中存储的即是路由映射内容。

我们在 `__init__` 方法的最后一行增加以下代码来看一下 mapper 的内容（路由映射的内容）：

```
        def format_methods(r):
            if r.conditions:                              
                method = r.conditions.get('method', '')
                return type(method) is str and method or ', '.join(method)
            else:
                return ''
        def get_mapper(mapper):
            file_object = open('/tmp/extension_mapper', 'w+')
            file_object.writelines("wlw============================Start Get ResourceMiddleware.mapper\n")
            file_object.writelines("Route name, Methods, Path, Controller, action\n")
            for r in mapper.matchlist:
                name = r.name or ''
                method = format_methods(r)
                path = r.routepath or ''
                action = r.defaults.get('action', '')
                file_object.writelines("%s, %s, %s, %s, %s\n" % (name, method, path, r.defaults.get('controller', ''), action))
            file_object.writelines('wlw============================End Get ResourceMiddleware.mapper')            file_object.close()
                                                          
        get_mapper(mapper)
```

重新启动 neutron-server 服务

*/tmp/extension_mapper* 文件内容为：

* 接下来，我们找到 `ExtensionMiddleware` 的 `__call__` 方法，我们发现这里依然是调用了 `routes.middleware.RoutesMiddleware` 中间件实例 `_router` 来实现访问 extension 的路由分发（由访问路径到返回处理方法 controller）。

`_router` 实例会进一步的调用了 `_dispatch` 返回匹配到的处理请求的 cotroller，我们在 `_dispatch` 中增加一条调试语句：

```
    @staticmethod
    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def _dispatch(req):
        """Dispatch the request.

        Returns the routed WSGI app's response or defers to the extended
        application.
        """
        LOG.info('wlw==========================ExtensionMiddleware._dsipatch.req.environ.wsgiorg.routing_args: %s ' % req.environ['wsgiorg.routing_args'][1])
...
```

* 我们用 curl 访问 neutron 来测试一下：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/availability_zones -H 'Content-Type: application/json' -H 'X-Auth-Token: 8a5310785b034ac7a37f4c19244e1e69' | jq
```

返回值为：

```
{
  "availability_zones": [
    {
      "state": "available",
      "resource": "router",
      "name": "nova"
    },
    {
      "state": "available",
      "resource": "network",
      "name": "nova"
    }
  ]
}
```

同时，在 neutron 的 log 中可以看到我们输出：

```
2017-04-28 23:04:46.671 ^[[00;36mINFO neutron.api.extensions [^[[01;36mreq-b16c0269-6541-47b5-b55e-476bcbf649cd ^[[00;36madmin d4edcc21aaca452dbc79e7a6056e53bb^[[00;36m] ^[[01;35m^[[00;36mwlw========================== req.environ.wsgiorg.routing_args: {'action': u'index', 'controller': <wsgify at 91861840 wrapping <function resource at 0x593c2a8>>} ^[[00m^M
```

那么我们对比以下刚才通过 pdb 过去的路由列表，找到我们这次访问的路由：

```
('availability_zones', 'GET', '/availability_zones', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'index')
```

_这里的 python 对象的 id 不一样，是因为中间重启了一次 neutron。_

## controller 的实现

* 那么下面我们就跟踪一下 controller 的调用，我们找一个 extension 的实例（例如 `Availability_zone`），我么就可以发现实现 controller 的是 `neutron.api.v2.resource.Resource` 方法：

`Resource`_ 是个方法，不是类，这个方法返回了一个可以处理 wsgi 消息的方法 _`resource`_。_

`Resource` 方法定义了解析消息体和构造消息体的方法，而且是对真正 controller 的一个封装。

我们在 `resource` 方法的第一行添加一条调试语句：

```
    def resource(request):
        LOG.info('wlw========================== Resource.resource')
...
```

* 上面我们说 `Resource` 方法只是对真正的 controller 的封装，那么真正的 controller 是用什么实现的呢？是 `neutron.api.v2.Controller`。

* 上面我们看 LOG 的输出，可以看到调用的 controller 的方法是 `index`，那么我们在 `neutron.api.v2.Controller.index` 中增加一条调试语句：

```
    @db_api.retry_db_errors
    def index(self, request, **kwargs):
        """Returns a list of the requested entity."""
        LOG.info('wlw=============================== Controller.index')
...
```

* 最后，我们依然用 curl 命令来访问 neutron：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/availability_zones -H 'Content-Type: application/json' -H 'X-Auth-Token: 7eff6dc843394c97ba9322d3bba44e96'
```

LOG 的输出为：

```
2017-04-30 10:41:24.733 ^[[00;36mINFO neutron.api.extensions [^[[01;36mreq-d65f5836-517c-4859-be44-6489277a83dc ^[[00;36madmin d4edcc21aaca452dbc79e7a6056e53bb^[[00;36m] ^[[01;35m^[[00;36mwlw==========================ExtensionMiddleware._dsipatch.req.environ.wsgiorg.routing_args: {'action': u'index', 'controller': <wsgify at 98849616 wrapping <function resource at 0x5fd5e60>>} ^[[00m^M
2017-04-30 10:41:24.734 ^[[00;36mINFO neutron.api.v2.resource [^[[01;36mreq-d65f5836-517c-4859-be44-6489277a83dc ^[[00;36madmin d4edcc21aaca452dbc79e7a6056e53bb^[[00;36m] ^[[01;35m^[[00;36mwlw========================== Resource.resource^[[00m^M
2017-04-30 10:41:24.735 ^[[00;36mINFO neutron.api.v2.base [^[[01;36mreq-d65f5836-517c-4859-be44-6489277a83dc ^[[00;36madmin d4edcc21aaca452dbc79e7a6056e53bb^[[00;36m] ^[[01;35m^[[00;36mwlw=============================== Controller.index^[[00m^M
```

## 总结：

我们总结一下：

1. paste.deploy 实现 wsgi 的基本框架

2. `ExtensionMiddleware` 利用 `routes.Mapper` 构造了路由映射，路由分发也是由这个类来实现的。

3. 路由分发后，我们找到 controller，找到 action。对这些调用后，返回消息体。



