# neutron 中 wsgi 映射关系的建立（资源的访问路径与后台的处理方法）

我们通过 [rest api](https://developer.openstack.org/api-ref/networking/v2/?expanded=bulk-create-networks-detail#networking-api-v2-0) 可以访问、删除、创造 neutron 的资源，那么当我们通过 rest api 发起一个请求时，后台是如何处理这个请求的？本文就来探讨这个问题。

```
curl -s -X GET http://172.16.100.106:9696/v2.0/networks \
-H "Content-Type: application/json" \
-H "X-Auth-Token: 7eb90d76addc4a5bafeb380bf47f37fd"
```

## core plugin 的 resource 的映射实现

```
col_kwargs = dict(collection_actions=COLLECTION_ACTIONS,
                          member_actions=MEMBER_ACTIONS)

def _map_resource(collection, resource, params, parent=None):
    allow_bulk = cfg.CONF.allow_bulk
    allow_pagination = cfg.CONF.allow_pagination
    allow_sorting = cfg.CONF.allow_sorting
    controller = base.create_resource(
        collection, resource, plugin, params, allow_bulk=allow_bulk,
        parent=parent, allow_pagination=allow_pagination,
        allow_sorting=allow_sorting)
    path_prefix = None
    if parent:
        path_prefix = "/%s/{%s_id}/%s" % (parent['collection_name'],
                                          parent['member_name'],
                                          collection)
    mapper_kwargs = dict(controller=controller,
                         requirements=REQUIREMENTS,
                         path_prefix=path_prefix,
                         **col_kwargs)
    return mapper.collection(collection, resource,
                             **mapper_kwargs)

for resource in RESOURCES:
    _map_resource(RESOURCES[resource], resource,
                  attributes.RESOURCE_ATTRIBUTE_MAP.get(
                      RESOURCES[resource], dict()))
    resource_registry.register_resource_by_name(resource)

for resource in SUB_RESOURCES:
    _map_resource(SUB_RESOURCES[resource]['collection_name'], resource,
                  attributes.RESOURCE_ATTRIBUTE_MAP.get(
                      SUB_RESOURCES[resource]['collection_name'],
                      dict()),
                  SUB_RESOURCES[resource]['parent'])
```

**作用：**对 `routes.Mapper().collection` 方法的封装，建立映射关系。

### 介绍一下在这里用到的 neutron.conf 中的三个配置选项：

 * `allow_bulk` 允许使用批量API（比如说我们可通过 reset api 批量创建网络）；
 * `allow_paginaion` 允许使用分页（已被丢弃的选项，恒为 True）;
 * `allow_sorting` 允许使用排序（已被丢弃的选项，恒为 True）;

```
# Allow the usage of the bulk API (boolean value)
#allow_bulk = true

# DEPRECATED: Allow the usage of the pagination. This option has been
# deprecated and will now be enabled unconditionally. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#allow_pagination = true

# DEPRECATED: Allow the usage of the sorting. This option has been deprecated
# and will now be enabled unconditionally. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#allow_sorting = true
```

### `routes.Mapper().collection` 使用示例

```
import routes

map = routes.Mapper()

collection = 'entries'
resource = 'entry'
controller = dict()
path_prefix = None
requirements = {'id': 'id', 'format': 'json'}
collection_actions = ['index', 'create']
member_actions = ['show', 'update', 'delete']

mapper_kwargs = dict(controller = controller,
requirements = requirements,
path_prefix = path_prefix,
collection_actions = collection_actions,
member_actions = member_actions)

map.collection(collection, resource, **mapper_kwargs)
```

那么我们构造的映射关系如下：

```
>>> print map
Route name Methods Path Controller action
entries GET /entries{.format} {} index
create_entry POST /entries{.format} {} create
entry GET /entries/{id}{.format} {} show
update_entry PUT /entries/{id}{.format} {} update
delete_entry DELETE /entries/{id}{.format} {} delete
```

```
RESOURCES = {'network': 'networks',
'subnet': 'subnets',
'subnetpool': 'subnetpools',
'port': 'ports'}
SUB_RESOURCES = {}
COLLECTION_ACTIONS = ['index', 'create']
MEMBER_ACTIONS = ['show', 'update', 'delete']
REQUIREMENTS = {'id': constants.UUID_PATTERN, 'format': 'json'}
```

## Controller 的构造

* `create_resource` 很简单，就是实现了一个 Controller 实例，并返回了一个 把 Controller 实例进行包装的 Resource实例。

```
def create_resource(collection, resource, plugin, params, allow_bulk=False,
                    member_actions=None, parent=None, allow_pagination=False,
                    allow_sorting=False):
    controller = Controller(plugin, collection, resource, params, allow_bulk,
                            member_actions=member_actions, parent=parent,
                            allow_pagination=allow_pagination,
                            allow_sorting=allow_sorting)

    return wsgi_resource.Resource(controller, FAULT_MAP)
```

### `neutron.api.v2.base.Controller` 

`neutron.api.v2.base.py` 就是实现了 Contrller 类和 create_resource 方法。

**`Controller` 是 neutron 中 wsgi 实现的关键类，我们一点点分析。**

*我们不是 neutron 架构的设计者，单看这个类的实现是很难理解其用处的，我么就结合其使用来看（见上面）。*

### `Controller` 的 `__init__`

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
```

* `_init_policy_attrs` 创建一个 policy 所需要的属性列表。

* `__init__` 方法主要是做了一些属性初始化的工作，一个主要的工作就是构造 `self._plugin_handlers`。
 
 * 如果我们的 `self._collection` 为 `ports`，`self._resource` 为 `port`，`self.parent` 为 `None`，那么我们得到的 `self._plugin_handlers` 将会是：

```
self._plugin_handlers = {
    self.list : get_ports,
    self.show : get_port,
    self.create : create_port,
    self.update : update_port,
    self.delete : delete_port}
```

### 获取 plugin 以及其 resource 属性的一些参数

```
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

### `__getattr__` 的实现

```
    def __getattr__(self, name):
        if name in self._member_actions:
            @db_api.retry_db_errors
            def _handle_action(request, id, **kwargs):
                arg_list = [request.context, id]
                # Ensure policy engine is initialized
                policy.init()
                # Fetch the resource and verify if the user can access it
                try:
                    parent_id = kwargs.get(self._parent_id_name)
                    resource = self._item(request,
                                          id,
                                          do_authz=True,
                                          field_list=None,
                                          parent_id=parent_id)
                except oslo_policy.PolicyNotAuthorized:
                    msg = _('The resource could not be found.')
                    raise webob.exc.HTTPNotFound(msg)
                body = kwargs.pop('body', None)
                # Explicit comparison with None to distinguish from {}
                if body is not None:
                    arg_list.append(body)
                # It is ok to raise a 403 because accessibility to the
                # object was checked earlier in this method
                policy.enforce(request.context,
                               name,
                               resource,
                               pluralized=self._collection)
                ret_value = getattr(self._plugin, name)(*arg_list, **kwargs)
                # It is simply impossible to predict whether one of this
                # actions alters resource usage. For instance a tenant port
                # is created when a router interface is added. Therefore it is
                # important to mark as dirty resources whose counters have
                # been altered by this operation
                resource_registry.set_resources_dirty(request.context)
                return ret_value

            return _handle_action
        else:
            raise AttributeError()
```