# routes.middleware – Routes WSGI Middleware

Routes WSGI Middleware

## Module Contents

```
 class routes.middleware.RoutesMiddleware(wsgi_app, mapper, use_method_override=True, path_info=True, singleton=True)
```

`RoutesMiddleware` 是一个 WSGI 中间件程序，它将路由匹配结果存到environ环境变量中去。

* 实例

```
from routes.middleware import RoutesMiddleware  
app = RoutesMiddleware(wsgi_app, map)     # ``map`` is a routes.Mapper. 
```

* map调用match匹配URL，并设置WSGI环境变量 

```
environ['wsgiorg.routing_args'] = ((url, match))  
environ['routes.route'] = route  
environ['routes.url'] = url  
```

*route为匹配到的路由，url为一个URLGenerator对象，match为匹配所得条目。*

* 一个实际的路由输出：

```
wsgiorg.routing_args = (<routes.util.URLGenerator object at 0x0287AFB0>,   
                        {'action': u'index', 'controller': <__main__.Resourse instance at 0x02876E40>})  
routes.route = <routes.route.Route object at 0x02871F10>  
routes.url = <routes.util.URLGenerator object at 0x0287AFB0>  
```

* 在 `use_method_override` 为 `True` 的情况下：

`RoutesMiddleware` 会对 `environ` 变量中的 `REQUEST_METHOD` 进行处理，在路由匹配完后再改回原来的 `REQUEST_METHOD`。

* 在 `path_info` 为 `True` 的情况下：

`RoutesMiddleware` 会将 `PATH_INFO` 和 `SCRIPT_NAME` 写入到 `environ` 变量中。

*这要求你构造的 router 里面含有 `path_info` 变量。*

```
map.connect('blog/*path_info', controller='blog', path_info='')
```

* singleton=True

路由匹配的方法不同。

* `RoutesMiddleware` 的实例就是一个可调用的 WSGI Application（可以看其 `__call__` 方法）。

## 参考

[routes.middleware – Routes WSGI Middleware](http://routes.readthedocs.io/en/latest/modules/middleware.html)

[ Routes RoutesMiddleware ](http://blog.csdn.net/spch2008/article/details/9005260)

