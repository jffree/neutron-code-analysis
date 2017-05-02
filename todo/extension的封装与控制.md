# extension 的封装与控制

在 [extension 架构](./extension架构.md) 中我们说到了有三种形式的 extension：

1. 直接实现了某种新的resource。比如实现了资源XXX，那么我可以通过/v2.0/XXX进行XXX资源的操作。这个是最类似于实现一个新的service_plugin的；

2. 对现有的某种资源添加某种操作功能。比如对于ports资源，我想有一个动作是做绑定（打个比方，不一定确切），则可以通过extension在现有的plugin基础上增加功能，比如对/v2.0/ports增加/action接口；

3. 对现有的某个REST API请求增加参数。比如对于/v2.0/ports我本来创建的时候什么参数都不用提供，现在我希望POST请求能带上参数NAME，则可以通过extension来实现；

## extension 的封装

*封装是为了统一管理。*

我们在分析 extension 基础类 `ExtensionDescriptor` 时，也提到了下面这三种方法：

1. `get_resources` 返回一个以 `extensions.ResourceExtension` 封装的资源列表。我们上面说了 extension 分为三类，那么第一类（暴露资源的 extension）必须实现这个方法。

2. `get_actions` 返回一个以 `extensions.ActionExtension` 封装的列表。这个是第二类 extension（暴露动作）必须实现的方法。

3. `get_request_extensions` 返回一个以 extensions.RequestException 封装的列表。这个是第三类 extension（暴露参数）必须实现的方法。

那么下面我们就分析一下这三类封装：

### `extensions.ResourceExtension` 

源码：

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

* `collection`：资源集合。一般是资源名称的复数形式（例如：`availability_zones`）。

 * collection （集合）这个词来自 `routes.Mapper` 的使用，相对于单个资源（比如说：水壶和水壶1号、水壶2号的区别）。

* `controller`：控制器。

 * 这个词也是来源于 `routes.Mapper` 的使用，意味着为接收到的请求的处理。

* `parent`：父资源。

* `path_prefix`：路径前缀。
 
 * 也是来源于对 `routes.Mapper` 的使用，在建立路由映射时，在所有的路径前增加的前缀。

* `collection_actions`：允许对 collection 的动作（index、delete等）。

* `member_actions`：允许对单个资源的动作。

* `attr_map`：资源的属性。

* `collection_methods`：允许对资源的请求方法（GET、PUT等）。

### `ActionExtension`

源码：

```
class ActionExtension(object):
    """Add custom actions to core Neutron OpenStack API controllers."""

    def __init__(self, collection, action_name, handler):
        self.collection = collection
        self.action_name = action_name
        self.handler = handler
```

* `collection`：同样是资源的复数；

* `action_name`：增加的动作的名称；

* `handler`：针对该动作名称调用的处理方法；

### `RequestExtension`

源码：

```
class RequestExtension(object):
    """Extend requests and responses of core Neutron OpenStack API controllers.

    Provide a way to add data to responses and handle custom request data
    that is sent to core Neutron OpenStack API controllers.
    """

    def __init__(self, method, url_route, handler):
        self.url_route = url_route
        self.handler = handler
        self.conditions = dict(method=[method])
        self.key = "%s-%s" % (method, url_route)
```

* `method`：请求方法；

* `url_routes`：请求路径；

* `handler`：对请求的处理方法。

## extension 控制器

我们有三种 extension，有三种 extension 的封装，那么自然我们就有三种 extenion 的控制器，用于处理 wsgi 的请求。

### `neutron.api.v2.resource` 中的 `Resource`

`Resource` 是对真正的 `controller` 的一个封装，在这里面定义了：

1. 接收消息体的解析方法 `deserializers`

2. 回复消息体的封装方法 `serializers`

3. 动作的状态 `action_status`

4. 错误的处理 `faults`，请参考：[Faults](https://developer.openstack.org/api-ref/networking/v2/?expanded=bulk-create-networks-detail#faults)

5. 最终在获取真正 controller 方法处理后的消息体后，组合消息头，返回消息。

源码：

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

#### `neutron.api.v2.base`  中的 `Controller`

这是本篇文章的重头戏，也就是真正的 controller，所有的 resource extension 都是使用这个类来实现控制器功能。

controller 的分析分为两部分，一个是 controller 的初始化，另一个是controller 实现的 action。

初始化自然是指 `__init__` 方法。

我们之前有一篇文章是 [extension调试](./extension调试.md)，里面有一个是跟踪路由映射，我们从打印出的路由映射中可以发现，controller 应该实现 `create`、`index`、`new`、`update`、`delete`、`edit`、`show`、`tenant`、`default` 这几个 action。

那么我们就从 `__init__` 看起。

##### 初始化 `__init__` 方法

```
class Controller(object):
    LIST = 'list'
    SHOW = 'show'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'

    @property
    def plugin(self):
        return self._plugin

    @property
    def resource(self):
        return self._resource

    @property
    def attr_info(self):
        return self._attr_info

    @property
    def member_actions(self):
        return self._member_actions

    def _init_policy_attrs(self):
        """Create the list of attributes required by policy.

        If the attribute map contains a tenant_id policy, then include
        project_id to bring the resource into the brave new world.

        :return: sorted list of attributes required by policy

        """
        policy_attrs = {name for (name, info) in self._attr_info.items()
                        if info.get('required_by_policy')}
        if 'tenant_id' in policy_attrs:
            policy_attrs.add('project_id')

        # Could use list(), but sorted() makes testing easier.
        return sorted(policy_attrs)

    def __init__(self, plugin, collection, resource, attr_info,
                 allow_bulk=False, member_actions=None, parent=None,
                 allow_pagination=False, allow_sorting=False):
        if member_actions is None:
            member_actions = []
        self._plugin = plugin
        self._collection = collection.replace('-', '_')
        self._resource = resource.replace('-', '_')
        self._attr_info = attr_info
        self._allow_bulk = allow_bulk
        self._allow_pagination = allow_pagination
        self._allow_sorting = allow_sorting
        self._native_bulk = self._is_native_bulk_supported()
        self._native_pagination = self._is_native_pagination_supported()
        self._native_sorting = self._is_native_sorting_supported()
        self._policy_attrs = self._init_policy_attrs()
        self._notifier = n_rpc.get_notifier('network')
        self._member_actions = member_actions
        self._primary_key = self._get_primary_key()
        if self._allow_pagination and self._native_pagination:
            # Native pagination need native sorting support
            if not self._native_sorting:
                raise exceptions.Invalid(
                    _("Native pagination depend on native sorting")
                )
            if not self._allow_sorting:
                LOG.info(_LI("Allow sorting is enabled because native "
                             "pagination requires native sorting"))
                self._allow_sorting = True
        self.parent = parent
        if parent:
            self._parent_id_name = '%s_id' % parent['member_name']
            parent_part = '_%s' % parent['member_name']
        else:
            self._parent_id_name = None
            parent_part = ''
        self._plugin_handlers = {
            self.LIST: 'get%s_%s' % (parent_part, self._collection),
            self.SHOW: 'get%s_%s' % (parent_part, self._resource)
        }
        for action in [self.CREATE, self.UPDATE, self.DELETE]:
            self._plugin_handlers[action] = '%s%s_%s' % (action, parent_part,
                                                         self._resource)

    def _get_primary_key(self, default_primary_key='id'):
        for key, value in six.iteritems(self._attr_info):
            if value.get('primary_key', False):
                return key
        return default_primary_key

    def _is_native_bulk_supported(self):
        native_bulk_attr_name = ("_%s__native_bulk_support"
                                 % self._plugin.__class__.__name__)
        return getattr(self._plugin, native_bulk_attr_name, False)

    def _is_native_pagination_supported(self):
        return api_common.is_native_pagination_supported(self._plugin)

    def _is_native_sorting_supported(self):
        return api_common.is_native_sorting_supported(self._plugin)
```

* `__init__` 参数说明：

 1. `plugin` 支持该 extention 的 plugin 实例；
 2. `collection` 资源复数名；
 3. `resource` 资源单数名；
 4. `attr_info` 资源属性；
 5. `allow_bulk` 是否允许批量操作；（一次对多个资源进行操作，参考：[Bulk-create](https://developer.openstack.org/api-ref/networking/v2/?expanded=bulk-create-networks-detail#bulk-create)）
 6. `member_actions` 允许对单个资源的动作；
 7. `parent` 父资源名；
 8. `allow_pagination` 是否允许分页；（限制服务器一次返回的资源个数，请参考：[Pagination](https://developer.openstack.org/api-ref/networking/v2/?expanded=bulk-create-networks-detail#pagination)）
 9. `allow_sorting` 是否允许排序；（对返回的资源列表进行排序，请参考：[Sorting](https://developer.openstack.org/api-ref/networking/v2/?expanded=bulk-create-networks-detail#sorting)）

* 我们看一下 `__init__` 方法都做了那些工作：

 1. 初始化控制器的一些参数

 2. 获得 plugin 的一些参数（`self._native_bulk`、`self._native_pagination`、`self._native_sorting`）

 3. 调用 `self._init_policy_attrs` 获取 policy 所需要的资源属性列表；

 4. 调用 `self._get_primary_key` 获取资源属性的主键

 5. 构造了 `self._plugin_handlers` 的字典；

创建 availability_zone resource extension 的 controller 时的  `self._plugin_handlers` 实例： `{'create': 'create_availability_zone', 'delete': 'delete_availability_zone', 'list': 'get_availability_zones', 'update': 'update_availability_zone', 'show': 'get_availability_zone'}`

##### `index` 动作

源码：

```
    @db_api.retry_db_errors
    def index(self, request, **kwargs):
        """Returns a list of the requested entity."""
        parent_id = kwargs.get(self._parent_id_name)
        # Ensure policy engine is initialized
        policy.init()
        return self._items(request, True, parent_id)
```

这里我们可以看到它在最后调用了 `_items` 方法，对于这个方法我们重点看这么几行：

```
    def _items(self, request, do_authz=False, parent_id=None):
    
    ....
    
        obj_getter = getattr(self._plugin, self._plugin_handlers[self.LIST])
        obj_list = obj_getter(request.context, **kwargs)
        obj_list = sorting_helper.sort(obj_list)
        obj_list = pagination_helper.paginate(obj_list)
        # Check authz
        if do_authz:
            # FIXME(salvatore-orlando): obj_getter might return references to
            # other resources. Must check authZ on them too.
            # Omit items from list that should not be visible
            obj_list = [obj for obj in obj_list
                        if policy.check(request.context,
                                        self._plugin_handlers[self.SHOW],
                                        obj,
                                        plugin=self._plugin,
                                        pluralized=self._collection)]
        # Use the first element in the list for discriminating which attributes
        # should be filtered out because of authZ policies
        # fields_to_add contains a list of attributes added for request policy
        # checks but that were not required by the user. They should be
        # therefore stripped
        fields_to_strip = fields_to_add or []
        if obj_list:
            fields_to_strip += self._exclude_attributes_by_policy(
                request.context, obj_list[0])
        collection = {self._collection:
                      [self._filter_attributes(
                          request.context, obj,
                          fields_to_strip=fields_to_strip)
                       for obj in obj_list]}
        pagination_links = pagination_helper.get_links(obj_list)
        if pagination_links:
            collection[self._collection + "_links"] = pagination_links
        # Synchronize usage trackers, if needed
        resource_registry.resync_resource(
            request.context, self._resource, request.context.tenant_id)
        return collection
```

看到这里我们就明白了， `_items` 方法从支持此 extension 的 plugin 里面获取属性方法 `obj_getter`，再通过此方法去处理请求，获取 `obj_list`，最终通过 `obj_list` 获取所有的返回值。

我们同时也明白了，`self._plugin_handlers` 保存的是需要从 plugin 里面获取的方法。

* 我们以 `Availability_zone` extension 为例，来看以下这个方法。
 1. 支持 `Availability_zone` extension 的 plugin 为 `Ml2Plugin`，也就是我们的核心插件
 2. 访问 `Availability_zone` extension controller 的 index 方法，需要调用 `Ml2Plugin` 插件的方法为：`get_availability_zones`。
 3. 我们在 `Ml2Plugin` 的 `__init__` 方法的初始位置设定断点（`pdb.set_trace()`），调试时使用下列语句获取 `Ml2Plugin` 的继承列表：`Ml2Plugin.mro()`，结果如下：
 ```
<class 'neutron.plugins.ml2.plugin.Ml2Plugin'>, <class 'neutron.db.db_base_plugin_v2.NeutronDbPluginV2'>, <class 'neutron.db.db_base_plugin_common.DbBasePluginCommon'>, <class 'neutron.neutron_plugin_base_v2.NeutronPluginBaseV2'>, <class 'neutron.worker.WorkerSupportServiceMixin'>, <class 'neutron.db.rbac_db_mixin.RbacPluginMixin'>, <class 'neutron.db.common_db_mixin.CommonDbMixin'>, <class 'neutron.db.standardattrdescription_db.StandardAttrDescriptionMixin'>, <class 'neutron.db.dvr_mac_db.DVRDbMixin'>, <class 'neutron.extensions.dvr.DVRMacAddressPluginBase'>, <class 'neutron.db.external_net_db.External_net_db_mixin'>, <class 'neutron.db.securitygroups_rpc_base.SecurityGroupServerRpcMixin'>, <class 'neutron.db.securitygroups_db.SecurityGroupDbMixin'>, <class 'neutron.extensions.securitygroup.SecurityGroupPluginBase'>, <class 'neutron.db.agentschedulers_db.AZDhcpAgentSchedulerDbMixin'>, <class 'neutron.db.agentschedulers_db.DhcpAgentSchedulerDbMixin'>, <class 'neutron.extensions.dhcpagentscheduler.DhcpAgentSchedulerPluginBase'>, <class 'neutron.db.agentschedulers_db.AgentSchedulerDbMixin'>, <class 'neutron.db.agents_db.AgentDbMixin'>, <class 'neutron.extensions.agent.AgentPluginBase'>, <class 'neutron.db.agents_db.AgentAvailabilityZoneMixin'>, <class 'neutron.extensions.availability_zone.AvailabilityZonePluginBase'>, <class 'neutron.db.availability_zone.network.NetworkAvailabilityZoneMixin'>, <class 'neutron.extensions.network_availability_zone.NetworkAvailabilityZonePluginBase'>, <class 'neutron.db.allowedaddresspairs_db.AllowedAddressPairsMixin'>, <class 'neutron.db.vlantransparent_db.Vlantransparent_db_mixin'>, <class 'neutron.db.extradhcpopt_db.ExtraDhcpOptMixin'>, <class 'neutron.db.address_scope_db.AddressScopeDbMixin'>, <class 'neutron.extensions.address_scope.AddressScopePluginBase'>, <class 'neutron.db.subnet_service_type_db_models.SubnetServiceTypeMixin'>, <type 'object'>)
 ```
 4. 我们在继承列表中发现了这么两个类：`<class 'neutron.db.agents_db.AgentAvailabilityZoneMixin'>` 和 `<class 'neutron.extensions.availability_zone.AvailabilityZonePluginBase'>`。
 5. 看一下 `<class 'neutron.extensions.availability_zone.AvailabilityZonePluginBase'>` 这个类，发现它定义了一个 `get_availability_zones` 抽象方法。
 6.‵<class 'neutron.db.agents_db.AgentAvailabilityZoneMixin'>` 类继承于 `<class 'neutron.extensions.availability_zone.AvailabilityZonePluginBase'>` 且实现了 `get_availability_zones` 方法，这个就是被 extension controller 调用的方法。




##### `create` 动作





##### 从给用户的响应中删除一些不可见（`'is_visible': False`）或者不符合 policy 检查的属性

`_exclude_attributes_by_policy` 方法用于返回一个应该被删除的属性列表。
 
```
    def _exclude_attributes_by_policy(self, context, data):
        """Identifies attributes to exclude according to authZ policies.

        Return a list of attribute names which should be stripped from the
        response returned to the user because the user is not authorized
        to see them.
        """
        attributes_to_exclude = []
        for attr_name in data.keys():
            # TODO(amotoki): At now, all attribute maps have tenant_id and
            # determine excluded attributes based on tenant_id.
            # We need to migrate tenant_id to project_id later
            # as attr_info is referred to in various places and we need
            # to check all logis carefully.
            if attr_name == 'project_id':
                continue
            attr_data = self._attr_info.get(attr_name)
            if attr_data and attr_data['is_visible']:
                if policy.check(
                    context,
                    '%s:%s' % (self._plugin_handlers[self.SHOW], attr_name),
                    data,
                    might_not_exist=True,
                    pluralized=self._collection):
                    # this attribute is visible, check next one
                    continue
            # if the code reaches this point then either the policy check
            # failed or the attribute was not visible in the first place
            attributes_to_exclude.append(attr_name)
            # TODO(amotoki): As mentioned in the above TODO,
            # we treat project_id and tenant_id equivalently.
            # This should be migrated to project_id in Ocata.
            if attr_name == 'tenant_id':
                attributes_to_exclude.append('project_id')

        return attributes_to_exclude
```




























### `ActionExtensionController`

这个是 action extension 的控制器，源码如下：

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

我们看一下在 `ExtensionMiddleware.__init__` 对它的调用：

```
# extended actions
        action_controllers = self._action_ext_controllers(application,
                                                          self.ext_mgr, mapper)
        for action in self.ext_mgr.get_actions():
            LOG.debug('Extended action: %s', action.action_name)
            controller = action_controllers[action.collection]
            controller.add_action(action.action_name, action.handler)
```

可以看出来，这里首先是为所有的 action extension 构建 controller，然后再为 controller 添加 handler。

### `RequestExtensionController`

这个是 requext extension 的控制器，源码如下：

```
class RequestExtensionController(wsgi.Controller):

    def __init__(self, application):
        self.application = application
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def process(self, request, *args, **kwargs):
        res = request.get_response(self.application)
        # currently request handlers are un-ordered
        for handler in self.handlers:
            response = handler(request, res)
        return response
```

对它的调用同样是在 `ExtensionMiddleware.__init__` 中：

```
        # extended requests
        req_controllers = self._request_ext_controllers(application,
                                                        self.ext_mgr, mapper)
        for request_ext in self.ext_mgr.get_request_extensions():
            LOG.debug('Extended request: %s', request_ext.key)
            controller = req_controllers[request_ext.key]
            controller.add_handler(request_ext.handler)
```

逻辑同 action extension 中是一致的。

### 一个特殊的控制器 `ExtensionController`

这个控制器是专门为 `extensions` 资源服务的，也就是所有资源的大管家：

我们先看一下它的使用，在 `ExtensionManager.get_resources` 中：


```
        resources.append(ResourceExtension('extensions',
                                           ExtensionController(self)))
```

很明显这是个手动增加的 extension，而不是自动从目录中增加的。

再看一下它的源码：

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

这个就是个典型的简单控制器了，实现了 `index`、`show`、`delete`、`create` 方法。

我们可以通过下面的方法访问这个资源：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/extensions -H 'Content-Type: application/json' -H 'X-Auth-Token: 189ad468b6054a03aea1d08538149576'
```

关于 `extensions`，请参考：[Extensions](https://developer.openstack.org/api-ref/networking/v2/?expanded=bulk-create-networks-detail#extensions) 