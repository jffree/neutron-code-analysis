# extensions filter

```
[filter:extensions]
paste.filter_factory = neutron.api.extensions:plugin_aware_extension_middleware_factory
```

* 找到 `plugin_aware_extension_middleware_factory`，在 `neutron.api.extensions` 模块中：

```
def plugin_aware_extension_middleware_factory(global_config, **local_config):
    """Paste factory."""
    def _factory(app):
        ext_mgr = PluginAwareExtensionManager.get_instance()
        return ExtensionMiddleware(app, ext_mgr=ext_mgr)
    return _factory
```

* 找到 `ExtensionMiddleware` 类，同样在 `neutron.api.extensions` 模块中：

```
class ExtensionMiddleware(base.ConfigurableMiddleware):
    """Extensions middleware for WSGI."""

    def __init__(self, application,
                 ext_mgr=None):
        self.ext_mgr = (ext_mgr
                        or ExtensionManager(get_extensions_path()))
        mapper = routes.Mapper()

        # extended resources
        for resource in self.ext_mgr.get_resources():
            path_prefix = resource.path_prefix
            if resource.parent:
                path_prefix = (resource.path_prefix +
                               "/%s/{%s_id}" %
                               (resource.parent["collection_name"],
                                resource.parent["member_name"]))

            LOG.debug('Extended resource: %s',
                      resource.collection)
            for action, method in six.iteritems(resource.collection_actions):
                conditions = dict(method=[method])
                path = "/%s/%s" % (resource.collection, action)
                with mapper.submapper(controller=resource.controller,
                                      action=action,
                                      path_prefix=path_prefix,
                                      conditions=conditions) as submap:
                    submap.connect(path_prefix + path, path)
                    submap.connect(path_prefix + path + "_format",
                                   "%s.:(format)" % path)

            for action, method in resource.collection_methods.items():
                conditions = dict(method=[method])
                path = "/%s" % resource.collection
                with mapper.submapper(controller=resource.controller,
                                      action=action,
                                      path_prefix=path_prefix,
                                      conditions=conditions) as submap:
                    submap.connect(path_prefix + path, path)
                    submap.connect(path_prefix + path + "_format",
                                   "%s.:(format)" % path)

            mapper.resource(resource.collection, resource.collection,
                            controller=resource.controller,
                            member=resource.member_actions,
                            parent_resource=resource.parent,
                            path_prefix=path_prefix)

        # extended actions
        action_controllers = self._action_ext_controllers(application,
                                                          self.ext_mgr, mapper)
        for action in self.ext_mgr.get_actions():
            LOG.debug('Extended action: %s', action.action_name)
            controller = action_controllers[action.collection]
            controller.add_action(action.action_name, action.handler)

        # extended requests
        req_controllers = self._request_ext_controllers(application,
                                                        self.ext_mgr, mapper)
        for request_ext in self.ext_mgr.get_request_extensions():
            LOG.debug('Extended request: %s', request_ext.key)
            controller = req_controllers[request_ext.key]
            controller.add_handler(request_ext.handler)

        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          mapper)
        super(ExtensionMiddleware, self).__init__(application)
```

## `for resource in self.ext_mgr.get_resources():`

* `get_resources` 方法在 `ExtensionManager` 中实现

```
    def get_resources(self):
        """Returns a list of ResourceExtension objects."""
        resources = []
        resources.append(ResourceExtension('extensions',
                                           ExtensionController(self)))
        for ext in self.extensions.values():
            resources.extend(ext.get_resources())
        return resources
```

* 我们可以进入每个 extension 类中查看一下 `get_resources`方法，发现它返回的也是一个 `ResourceExtension` 的对象列表，那么我们看一下 `ResourceExtension` 的实现：

```
class ResourceExtension(object):
    """Add top level resources to the OpenStack API in Neutron."""

    def __init__(self, collection, controller, parent=None, path_prefix="",
                 collection_actions=None, member_actions=None, attr_map=None,
                 collection_methods=None):
        collection_actions = collection_actions or {}
        collection_methods = collection_methods or {}
        member_actions = member_actions or {}
        attr_map = attr_map or {}
        self.collection = collection
        self.controller = controller
        self.parent = parent
        self.collection_actions = collection_actions
        self.collection_methods = collection_methods
        self.member_actions = member_actions
        self.path_prefix = path_prefix
        self.attr_map = attr_map
```

* 好吧，这个使我们到目前为止见到的一个最简的类了。如果你对 `routes.Mapper().collection` 方法足够熟悉的话，那么很轻易的看出来 `ResourceExtension` 是对该方法参数的一个封装：

```
collection(self, collection_name, resource_name, path_prefix=None, member_prefix='/{id}', controller=None, collection_actions=['index', 'create', 'new'], member_actions=['show', 'update', 'delete', 'edit'], member_options=None, **kwargs) 
    method of routes.mapper.Mapper instance
    Create a submapper that represents a collection.
    ....
```

* 这里的每项的含义是：

 * `self.collection`：资源复数的名字，比如ports、networks。在REST API中，url一般是复数的，比如GET /v2.0/ports，复数的GET一般是通过filter来获取信息，而单数的GET，如/v2.0/ports/{id}则是通过id号获取

 * `self.controller`：资源代表的controller，用于url和action的映射

 * `self.parent`：父资源

 * `self.collection_actions`：复数资源允许的REST API操作，比如ports允许哪些操作（SHOW、INDEX这类，可以看下上面的map.collection）

 * `self.member_actions`：单个资源允许的REST API操作，比如port允许哪些操作，在URL中一般是包含{id}的

 * `self.path_prefix`：url前缀

 * `self.attr_map`：REST API参数属性信息

## resource 中的第一项 `extensions`

* 我们再回去看 `ExtensionManager` 的 `get_resources` 方法，其中有这么两行代码：

```
...
        resources.append(ResourceExtension('extensions',
                                           ExtensionController(self)))
...
```

我们用 rest api 访问以下 `v2.0/extensions` 路径：

```
curl -s -X GET 172.16.100.106:9696/v2.0/extensions \
            -H "Content-Type: application/json" \
            -H "X-Auth-Token: c54521031ba540b0b183a5b26f82ab3d"
```













