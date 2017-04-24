# filter extensions

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
## extension 实现的三个功能：

1. 直接实现了某种新的resource。比如实现了资源XXX，那么我可以通过/v2.0/XXX进行XXX资源的操作。这个是最类似于实现一个新的service_plugin的

2. 对现有的某种资源添加某种操作功能。比如对于ports资源，我想有一个动作是做绑定（打个比方，不一定确切），则可以通过extension在现有的plugin基础上增加功能，比如对/v2.0/ports增加/action接口

3. 对现有的某个REST API请求增加参数。比如对于/v2.0/ports我本来创建的时候什么参数都不用提供，现在我希望POST请求能带上参数NAME，则可以通过extension来实现

*对于 1 和 2 ，我们都是要提供url的，所以这里应该就会做这个事情。从注释中也可看到，先是实现‘extended resources’，然后是‘extended actions’，最后是‘extended requests’。*

## `for resource in self.ext_mgr.get_resources():`

* `get_resources` 方法在 `ExtensionManager` 中实现

```py
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

* 我们用 rest api 访问以下 `v2.0/extensions` 路径：

```
curl -s -X GET 172.16.100.106:9696/v2.0/extensions \
            -H "Content-Type: application/json" \
            -H "X-Auth-Token: c54521031ba540b0b183a5b26f82ab3d"
```

### 我们接着看 `ExtensionController` 的实现

```
class ExtensionController(wsgi.Controller):

    def __init__(self, extension_manager):
        self.extension_manager = extension_manager

    @staticmethod
    def _translate(ext):
        ext_data = {}
        ext_data['name'] = ext.get_name()
        ext_data['alias'] = ext.get_alias()
        ext_data['description'] = ext.get_description()
        ext_data['updated'] = ext.get_updated()
        ext_data['links'] = []  # TODO(dprince): implement extension links
        return ext_data

    def index(self, request):
        extensions = []
        for _alias, ext in six.iteritems(self.extension_manager.extensions):
            extensions.append(self._translate(ext))
        return dict(extensions=extensions)

    def show(self, request, id):
        # NOTE(dprince): the extensions alias is used as the 'id' for show
        ext = self.extension_manager.extensions.get(id, None)
        if not ext:
            raise webob.exc.HTTPNotFound(
                _("Extension with alias %s does not exist") % id)
        return dict(extension=self._translate(ext))

    def delete(self, request, id):
        msg = _('Resource not found.')
        raise webob.exc.HTTPNotFound(msg)

    def create(self, request):
        msg = _('Resource not found.')
        raise webob.exc.HTTPNotFound(msg)
```

* 这里我们看一下 `index` 方法，这个方法其实就是将所有的 extension 的相关信息收集在一个集合中，`index` 的处理结果和我们的通过 rest api GET 方法访问 `/v2.0/extensions` 的到的结果是一致的。

* 至于 `show` 方法，则是针对单个的 extension 进行访问 `/v2.0/extensions/{alias}`：

```
curl -s -X GET 172.16.100.106:9696/v2.0/extensions/project-id \
              -H "Content-Type: application/json" \
              -H "X-Auth-Token: 15d4b89f42b048beae52ca7cd35ed664"
```

* `delete` 和 `create` 方法仅仅是返回一个错误页面。

## extended resources wsgi 映射关系的建立

上面分析了 resource 的整合以及 extensions 的映射关系，下面我们分析所有的 resources 的映射关系是如何建立的：

```
...
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
...
```

上文中还提到了这么一个事实：我们获取的 resources 实际上是一系列 `ResourceExtension` 实例的集合。

那么我们先不管一个具体的 resource 是如何构造的，我们单根据 `ResourceExtension` 来理解 resource 映射关系的构成。

看代码就知道映射实现的关键就在于 routes 模块的使用。其中，`submapper` 方法用于类似路由的添加。下面举例说一下 `resource` 方法：

* 第一个例子：

```
import routes

map = routes.Mapper()

map.resource('message', 'messages')
```

查看映射结果：

```
>>> print map
Route name             Methods Path                           Controller action
                       POST    /messages.:(format)            messages   create
                       POST    /messages                      messages   create
formatted_messages     GET     /messages.:(format)            messages   index 
messages               GET     /messages                      messages   index 
formatted_new_message  GET     /messages/new.:(format)        messages   new   
new_message            GET     /messages/new                  messages   new   
                       PUT     /messages/:(id).:(format)      messages   update
                       PUT     /messages/:(id)                messages   update
                       DELETE  /messages/:(id).:(format)      messages   delete
                       DELETE  /messages/:(id)                messages   delete
formatted_edit_message GET     /messages/:(id)/edit.:(format) messages   edit  
edit_message           GET     /messages/:(id)/edit           messages   edit  
formatted_message      GET     /messages/:(id).:(format)      messages   show  
message                GET     /messages/:(id)                messages   show 
```

* 第二个例子：

```
import routes

mapper = routes.Mapper()

controller='con'
member_actions={'default': 'GET'}
parent=None
map.resource('message', 'messages', controller=controller)

mapper.resource('message', 'messages',
                controller=controller,
                member=member_actions,
                parent_resource = parent,
                path_prefix = None)
```

查看映射结果：

```
>>> print mapper
Route name                Methods Path                              Controller action 
                          POST    /messages.:(format)               con        create 
                          POST    /messages                         con        create 
formatted_messages        GET     /messages.:(format)               con        index  
messages                  GET     /messages                         con        index  
formatted_new_message     GET     /messages/new.:(format)           con        new    
new_message               GET     /messages/new                     con        new    
                          PUT     /messages/:(id).:(format)         con        update 
                          PUT     /messages/:(id)                   con        update 
                          DELETE  /messages/:(id).:(format)         con        delete 
                          DELETE  /messages/:(id)                   con        delete 
formatted_default_message GET     /messages/:(id)/default.:(format) con        default
default_message           GET     /messages/:(id)/default           con        default
formatted_edit_message    GET     /messages/:(id)/edit.:(format)    con        edit   
edit_message              GET     /messages/:(id)/edit              con        edit   
formatted_message         GET     /messages/:(id).:(format)         con        show   
message                   GET     /messages/:(id)                   con        show 
```

* 就这样，通过 `routes.Mapper().submapper` 和 `routes.Mapper().resource` 实现了 extended resources wsgi 映射关系的建立。

## extended actions wsgi 映射关系的建立

```
...
        # extended actions
        action_controllers = self._action_ext_controllers(application,
                                                          self.ext_mgr, mapper)
        for action in self.ext_mgr.get_actions():
            LOG.debug('Extended action: %s', action.action_name)
            controller = action_controllers[action.collection]
            controller.add_action(action.action_name, action.handler)
...
```

* `_action_ext_controllers` 同样是在本类中实现

```
    def _action_ext_controllers(self, application, ext_mgr, mapper):
        """Return a dict of ActionExtensionController-s by collection."""
        action_controllers = {}
        for action in ext_mgr.get_actions():
            if action.collection not in action_controllers.keys():
                controller = ActionExtensionController(application)
                mapper.connect("/%s/:(id)/action.:(format)" %
                               action.collection,
                               action='action',
                               controller=controller,
                               conditions=dict(method=['POST']))
                mapper.connect("/%s/:(id)/action" % action.collection,
                               action='action',
                               controller=controller,
                               conditions=dict(method=['POST']))
                action_controllers[action.collection] = controller

        return action_controllers
```

* `ExtensionManager.get_actions` 方法如下：

```
    def get_actions(self):
        """Returns a list of ActionExtension objects."""
        actions = []
        for ext in self.extensions.values():
            actions.extend(ext.get_actions())
        return actions
```

*我在 neutron 的源代码中搜了一下，貌似只有测试时用到了 extension 的 get_actions 的方法。*

* `ActionExtension` 实现如下：

```
class ActionExtension(object):
    """Add custom actions to core Neutron OpenStack API controllers."""

    def __init__(self, collection, action_name, handler):
        self.collection = collection
        self.action_name = action_name
        self.handler = handler
```

* `ActionExtensionController` 的实现如下：

```
class ActionExtensionController(wsgi.Controller):

    def __init__(self, application):
        self.application = application
        self.action_handlers = {}

    def add_action(self, action_name, handler):
        self.action_handlers[action_name] = handler

    def action(self, request, id):
        input_dict = self._deserialize(request.body,
                                       request.get_content_type())
        for action_name, handler in six.iteritems(self.action_handlers):
            if action_name in input_dict:
                return handler(input_dict, request, id)
        # no action handler found (bump to downstream application)
        response = self.application
        return response
```

`ActionExtensionController` 的实现比较简单，也就是定义了一个 `action_handlers` 来保存请求方法和处理方法的映射关系，在 `action` 方法中解析请求消息体，若找到对应的请求方法，则对其进行处理。 

