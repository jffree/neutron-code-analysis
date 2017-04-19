# oslo_service 之 wsgi

*本文分析 oslo_service 模块中 wsgi 的实现。路径： `oslo_service.wsgi.py`*

## class Router(object)

**作用：** 用作 WSGI 的中间件，实现访问路径与实现方法的匹配

* 代码如下（删掉注释）：

*其实注释可以给我们提供相当有用的信息，我这里因为篇幅的原因就不再列出。*

```
class Request(webob.Request):
    pass

class Router(object):
    """WSGI middleware that maps incoming requests to WSGI apps."""

    def __init__(self, mapper):
        self.map = mapper
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.map)

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        return self._router

    @staticmethod
    @webob.dec.wsgify(RequestClass=Request)
    def _dispatch(req):
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app
```

1. `Request` 是对 `webob.Request` 的一个简单封装

2. `mapper`可以理解为访问路径与实现方法的匹配列表，在 openstack 中，都是传入一个 `routes.Mapper() ` 的实例

3. 实现了 `__call__` 方法，返回一个 `RoutesMiddleware` 的实例 `_router`。

4. `RoutesMiddleware` 是一个 WSGI 中间件，实现了 `__call__`方法。若对其实例 `_router`进行调用会将路由匹配结果存到environ环境变量中，进而调用 `_dispatch` 方法将匹配到的 wsgi 应用返回。

## 异常处理

```
class ConfigNotFound(Exception):
    def __init__(self, path):
        msg = _('Could not find config at %(path)s') % {'path': path}
        super(ConfigNotFound, self).__init__(msg)


class PasteAppNotFound(Exception):
    def __init__(self, name, path):
        msg = (_("Could not load paste app '%(name)s' from %(path)s") %
               {'name': name, 'path': path})
        super(PasteAppNotFound, self).__init__(msg)
```

## class Loader(object)

**作用：** 从 paste 的配置中根据 WSGI 应用的 name 导入该应用

* 代码

```
class Loader(object):
    """Used to load WSGI applications from paste configurations."""

    def __init__(self, conf):
        conf.register_opts(_options.wsgi_opts)
        self.config_path = None

        config_path = conf.api_paste_config
        if not os.path.isabs(config_path):
            self.config_path = conf.find_file(config_path)
        elif os.path.exists(config_path):
            self.config_path = config_path

        if not self.config_path:
            raise ConfigNotFound(path=config_path)

    def load_app(self, name):
        try:
            LOG.debug("Loading app %(name)s from %(path)s",
                      {'name': name, 'path': self.config_path})
            return deploy.loadapp("config:%s" % self.config_path, name=name)
        except LookupError:
            LOG.exception("Couldn't lookup app: %s", name)
            raise PasteAppNotFound(name=name, path=self.config_path)
```