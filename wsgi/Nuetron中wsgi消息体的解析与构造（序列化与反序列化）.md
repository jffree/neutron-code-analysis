# wsgi 消息体的解析与构造（序列化与反序列化）

```
class Request(wsgi.Request):
    pass


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

* 注意看清楚，这个 `Resource` 是个方法，不是个类；

## 参数

* `controller` 控制器（`neutron.api.v2.base.Controller`）实例 

* `faults`  错误的处理方式

* `deserializers` 消息解析器

* `serializers` 消息序列化器

* `action_status` 请求状态

## 代码解析

* Resource 的内部实现了一个 resource 的 wsgi app。

* resource 中利用消息解析器解析消息体

* resource 中利用消息序列化器封装请求的处理结果

* resource 用 `webob.Response` 封装响应并返回


















