extension 调试过程：

1. `api-paste.ini` 找到 `extensions filter` 

2. `neutron.api.extension` 找到  `plugin_aware_extension_middleware_factory`

3. 在 `neutron.api.extension` 找到 `ExtensionMiddleware`

4. 找到 `ExtensionMiddleware` 的 `__call__` 方法，我们发现这里依然是使用了 `routes.middleware.RoutesMiddleware` 中间件来实现路径路由。

5. 接着向下，我们找到了 `_dispatch` 方法，这里就实现了对请求的处理。我们就在这个 `_dispatch` 方法里面增加一条调试语句：｀LOG.info('wlw========================== ExtensionMiddleware._dispatch: %s ' % req.environ)｀。

6. 我们用 curl 来访问以下 neutron：
```
curl -s -X GET http://172.16.100.106:9696//v2.0/availability_zones -H 'Content-Type: application/json' -H 'X-Auth-Token: 8a5310785b034ac7a37f4c19244e1e69'
```

7. 