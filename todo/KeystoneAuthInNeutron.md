# keystone auth in neutron

在 api-paste.ini 中有这么一个过滤器

```
[filter:keystonecontext]
paste.filter_factory = neutron.auth:NeutronKeystoneContext.factory
```

若是我们的 neutron 走 keystone 认证的话，就会启用这个过滤器。

`NeutronKeystoneContext` 继承于 `oslo_middleware` 的 `ConfigurableMiddleware` 类，重写了 `ConfigurableMiddleware` 的 `__call__` 方法，我们从这里看起。

## `ConfigurableMiddleware.factory`

```
    @classmethod
    def factory(cls, global_conf, **local_conf):
        """Factory method for paste.deploy.

        :param global_conf: dict of options for all middlewares
                            (usually the [DEFAULT] section of the paste deploy
                            configuration file)
        :param local_conf: options dedicated to this middleware
                           (usually the option defined in the middleware
                           section of the paste deploy configuration file)
        """
        conf = global_conf.copy() if global_conf else {}
        conf.update(local_conf)

        def middleware_filter(app):
            return cls(app, conf)

        return middleware_filter
```

* 根据 paste.deploy 的配置文件初始化 `ConfigurableMiddleware`


## `ConfigurableMiddleware.__init__`

```
    def __init__(self, application, conf=None):
        """Base middleware constructor

        :param  conf: a dict of options or a cfg.ConfigOpts object
        """
        self.application = application

        # NOTE(sileht): If the configuration come from oslo.config
        # just use it.
        if isinstance(conf, cfg.ConfigOpts):
            self.conf = {}
            self.oslo_conf = conf
        else:
            self.conf = conf or {}
            if "oslo_config_project" in self.conf:
                if 'oslo_config_file' in self.conf:
                    default_config_files = [self.conf['oslo_config_file']]
                else:
                    default_config_files = None

                if 'oslo_config_program' in self.conf:
                    program = self.conf['oslo_config_program']
                else:
                    program = None

                self.oslo_conf = cfg.ConfigOpts()
                self.oslo_conf([],
                               project=self.conf['oslo_config_project'],
                               prog=program,
                               default_config_files=default_config_files,
                               validate_default_values=True)

            else:
                # Fallback to global object
                self.oslo_conf = cfg.CONF
```

`__init__` 方法主要是做了初始化 oslo_conf 的工作（cfg.ConfigOpts的实例）。

## `NeutronKeystoneContext.__call__`

```
    @webob.dec.wsgify
    def __call__(self, req):
        # Determine the user ID
        user_id = req.headers.get('X_USER_ID')
        if not user_id:
            LOG.debug("X_USER_ID is not found in request")
            return webob.exc.HTTPUnauthorized()

        # Determine the tenant
        tenant_id = req.headers.get('X_PROJECT_ID')

        # Suck out the roles
        roles = [r.strip() for r in req.headers.get('X_ROLES', '').split(',')]

        # Human-friendly names
        tenant_name = req.headers.get('X_PROJECT_NAME')
        user_name = req.headers.get('X_USER_NAME')

        # Use request_id if already set
        req_id = req.environ.get(request_id.ENV_REQUEST_ID)

        # Get the auth token
        auth_token = req.headers.get('X_AUTH_TOKEN',
                                     req.headers.get('X_STORAGE_TOKEN'))

        # Create a context with the authentication data
        ctx = context.Context(user_id, tenant_id, roles=roles,
                              user_name=user_name, tenant_name=tenant_name,
                              request_id=req_id, auth_token=auth_token)

        # Inject the context...
        req.environ['neutron.context'] = ctx

        return self.application
```

很明显，这里是根据认证的结果来构造一个上下文对象（`Context` 的实例）。

这个 `Context` 对象的构造十分的重要这在后面会被很多的地方用到。

#  context 的传递

看过我之前写的关于 neutron wsgi 实现的文章可以知道，所有的 wsgi 中的 controller 都是在这里实现的：

```
def Resource(controller, faults=None, deserializers=None, serializers=None,
             action_status=None):
    """Represents an API entity resource and the associated serialization and
    deserialization logic
    """
    default_deserializers = {'application/json': wsgi.JSONDeserializer()}
    default_serializers = {'application/json': wsgi.JSONDictSerializer()}
    format_types = {'json': 'application/json'}
    action_status = action_status or dict(create=201, delete=204)

    default_deserializers.update(deserializers or {})
    default_serializers.update(serializers or {})

    deserializers = default_deserializers
    serializers = default_serializers
    faults = faults or {}

    @webob.dec.wsgify(RequestClass=Request)
    def resource(request):
        route_args = request.environ.get('wsgiorg.routing_args')
        if route_args:
            args = route_args[1].copy()
        else:
            args = {}

        # NOTE(jkoelker) by now the controller is already found, remove
        #                it from the args if it is in the matchdict
        args.pop('controller', None)
        fmt = args.pop('format', None)
        action = args.pop('action', None)
        content_type = format_types.get(fmt,
                                        request.best_match_content_type())
        language = request.best_match_language()
        deserializer = deserializers.get(content_type)
        serializer = serializers.get(content_type)

        try:
            if request.body:
                args['body'] = deserializer.deserialize(request.body)['body']

            method = getattr(controller, action)

            result = method(request=request, **args)
        except Exception as e:
            mapped_exc = api_common.convert_exception_to_http_exc(e, faults,
                                                                  language)
            if hasattr(mapped_exc, 'code') and 400 <= mapped_exc.code < 500:
                LOG.info(_LI('%(action)s failed (client error): %(exc)s'),
                         {'action': action, 'exc': mapped_exc})
            else:
                LOG.exception(
                    _LE('%(action)s failed: %(details)s'),
                    {
                        'action': action,
                        'details': utils.extract_exc_details(e),
                    }
                )
            raise mapped_exc

        status = action_status.get(action, 200)
        body = serializer.serialize(result)
        # NOTE(jkoelker) Comply with RFC2616 section 9.7
        if status == 204:
            content_type = ''
            body = None

        return webob.Response(request=request, status=status,
                              content_type=content_type,
                              body=body)
    # NOTE(blogan): this is something that is needed for the transition to
    # pecan.  This will allow the pecan code to have a handle on the controller
    # for an extension so it can reuse the code instead of forcing every
    # extension to rewrite the code for use with pecan.
    setattr(resource, 'controller', controller)
    return resource
```
 
这里面有一个关于 `Request` 的装饰器的使用：

```
    @webob.dec.wsgify(RequestClass=Request)
```

我们跟踪下去：

## Class Request

```
class Request(wsgi.Request):
    pass
```

## wsgi.Request

```
class Request(wsgi.Request):

    def best_match_content_type(self):
        """Determine the most acceptable content-type.

        Based on:
            1) URI extension (.json)
            2) Content-type header
            3) Accept* headers
        """
        # First lookup http request path
        parts = self.path.rsplit('.', 1)
        if len(parts) > 1:
            _format = parts[1]
            if _format in ['json']:
                return 'application/{0}'.format(_format)

        #Then look up content header
        type_from_header = self.get_content_type()
        if type_from_header:
            return type_from_header
        ctypes = ['application/json']

        #Finally search in Accept-* headers
        bm = self.accept.best_match(ctypes)
        return bm or 'application/json'

    def get_content_type(self):
        allowed_types = ("application/json",)
        if "Content-Type" not in self.headers:
            LOG.debug("Missing Content-Type")
            return None
        _type = self.content_type
        if _type in allowed_types:
            return _type
        return None

    def best_match_language(self):
        """Determines best available locale from the Accept-Language header.

        :returns: the best language match or None if the 'Accept-Language'
                  header was not available in the request.
        """
        if not self.accept_language:
            return None
        all_languages = oslo_i18n.get_available_languages('neutron')
        return self.accept_language.best_match(all_languages)

    @property
    def context(self):
        if 'neutron.context' not in self.environ:
            self.environ['neutron.context'] = context.get_admin_context()
        return self.environ['neutron.context']
```

我们可以看到这个类中有一个 `context` 的属性方法，这个就是将刚才我们构造的 `Context` 实例返回。