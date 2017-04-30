# extension 调试过程：

## wsgi 框架

* `api-paste.ini` 找到 `extensions filter`

* `neutron.api.extension` 找到 `plugin_aware_extension_middleware_factory`。（根据 paste.deploy 的使用， filter 是接受一个 aap 为参数再返回一个 app。）

## 构造路由映射，分发路由请求

* 通过 `plugin_aware_extension_middleware_factory` 找到 `ExtensionMiddleware`，这个 filter 返回的就是 `ExtensionMiddleware` 实例为 app。

* 在 `ExtensionMiddleware` 的 `__init__` 方法中利用 `routes.Mapper` 实现了 extension 路由映射， `mapper` 变量中存储的即是路由映射内容。

我们在 `__init__` 方法的最后一行增加以下代码来看一下 mapper 的内容（路由映射的内容）：

```
LOG.info('wlw============================Start Get ResourceMiddleware.mapper')
def format_methods(r):
if r.conditions:
method = r.conditions.get('method', '')
return type(method) is str and method or ', '.join(method)
else:
return ''
def get_mapper(mapper):
print ('Route name', 'Methods', 'Path', 'Controller', 'action')
for r in mapper.matchlist:
print (r.name or '', format_methods(r), r.routepath or '',
r.defaults.get('controller', ''), r.defaults.get('action', ''))

import pdb
pdb.set_trace()
LOG.info('wlw============================Start Get ResourceMiddleware.mapper')
```

重新启动 neutron server，会进入调试模式，在这里我们调用我们写的 `get_mapper` 方法：

```
2017-04-28 22:53:11.570 INFO neutron.api.extensions [-] wlw============================Start Get ResourceMiddleware.mapper
> /opt/stack/neutron/neutron/api/extensions.py(377)__init__()
-> LOG.info('wlw============================Start Get ResourceMiddleware.mapper')
(Pdb) get_mapper(mapper)
```

输出结果为：

```
('Route name', 'Methods', 'Path', 'Controller', 'action')
('', 'POST', '/extensions.:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'create')
('', 'POST', '/extensions', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'create')
('formatted_extensions', 'GET', '/extensions.:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'index')
('extensions', 'GET', '/extensions', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'index')
('formatted_new_extensions', 'GET', '/extensions/new.:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'new')
('new_extensions', 'GET', '/extensions/new', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'new')
('', 'PUT', '/extensions/:(id).:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'update')
('', 'PUT', '/extensions/:(id)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'update')
('', 'DELETE', '/extensions/:(id).:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'delete')
('', 'DELETE', '/extensions/:(id)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'delete')
('formatted_edit_extensions', 'GET', '/extensions/:(id)/edit.:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'edit')
('edit_extensions', 'GET', '/extensions/:(id)/edit', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'edit')
('formatted_extensions', 'GET', '/extensions/:(id).:(format)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'show')
('extensions', 'GET', '/extensions/:(id)', <neutron.api.extensions.ExtensionController object at 0x5b933d0>, u'show')
('', 'POST', '/network-ip-availabilities.:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'create')
('', 'POST', '/network-ip-availabilities', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'create')
('formatted_network-ip-availabilities', 'GET', '/network-ip-availabilities.:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'index')
('network-ip-availabilities', 'GET', '/network-ip-availabilities', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'index')
('formatted_new_network-ip-availabilities', 'GET', '/network-ip-availabilities/new.:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'new')
('new_network-ip-availabilities', 'GET', '/network-ip-availabilities/new', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'new')
('', 'PUT', '/network-ip-availabilities/:(id).:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'update')
('', 'PUT', '/network-ip-availabilities/:(id)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'update')
('', 'DELETE', '/network-ip-availabilities/:(id).:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'delete')
('', 'DELETE', '/network-ip-availabilities/:(id)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'delete')
('formatted_edit_network-ip-availabilities', 'GET', '/network-ip-availabilities/:(id)/edit.:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'edit')
('edit_network-ip-availabilities', 'GET', '/network-ip-availabilities/:(id)/edit', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'edit')
('formatted_network-ip-availabilities', 'GET', '/network-ip-availabilities/:(id).:(format)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'show')
('network-ip-availabilities', 'GET', '/network-ip-availabilities/:(id)', <wsgify at 96024464 wrapping <function resource at 0x5d30d70>>, u'show')
('', 'POST', '/auto-allocated-topology.:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'create')
('', 'POST', '/auto-allocated-topology', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'create')
('formatted_auto-allocated-topology', 'GET', '/auto-allocated-topology.:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'index')
('auto-allocated-topology', 'GET', '/auto-allocated-topology', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'index')
('formatted_new_auto-allocated-topology', 'GET', '/auto-allocated-topology/new.:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'new')
('new_auto-allocated-topology', 'GET', '/auto-allocated-topology/new', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'new')
('', 'PUT', '/auto-allocated-topology/:(id).:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'update')
('', 'PUT', '/auto-allocated-topology/:(id)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'update')
('', 'DELETE', '/auto-allocated-topology/:(id).:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'delete')
('', 'DELETE', '/auto-allocated-topology/:(id)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'delete')
('formatted_edit_auto-allocated-topology', 'GET', '/auto-allocated-topology/:(id)/edit.:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'edit')
('edit_auto-allocated-topology', 'GET', '/auto-allocated-topology/:(id)/edit', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'edit')
('formatted_auto-allocated-topology', 'GET', '/auto-allocated-topology/:(id).:(format)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'show')
('auto-allocated-topology', 'GET', '/auto-allocated-topology/:(id)', <wsgify at 96025232 wrapping <function resource at 0x5d30de8>>, u'show')
('', 'POST', '/agents.:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'create')
('', 'POST', '/agents', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'create')
('formatted_agents', 'GET', '/agents.:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'index')
('agents', 'GET', '/agents', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'index')
('formatted_new_agents', 'GET', '/agents/new.:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'new')
('new_agents', 'GET', '/agents/new', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'new')
('', 'PUT', '/agents/:(id).:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'update')
('', 'PUT', '/agents/:(id)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'update')
('', 'DELETE', '/agents/:(id).:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'delete')
('', 'DELETE', '/agents/:(id)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'delete')
('formatted_edit_agents', 'GET', '/agents/:(id)/edit.:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'edit')
('edit_agents', 'GET', '/agents/:(id)/edit', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'edit')
('formatted_agents', 'GET', '/agents/:(id).:(format)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'show')
('agents', 'GET', '/agents/:(id)', <wsgify at 96025808 wrapping <function resource at 0x5d30e60>>, u'show')
('', 'POST', '/agents/{agent_id}/l3-routers.:(format)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'create')
('', 'POST', '/agents/{agent_id}/l3-routers', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'create')
('formatted_agent_l3-routers', 'GET', '/agents/{agent_id}/l3-routers.:(format)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'index')
('agent_l3-routers', 'GET', '/agents/{agent_id}/l3-routers', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'index')
('formatted_agent_new_l3-routers', 'GET', '/agents/{agent_id}/l3-routers/new.:(format)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'new')
('agent_new_l3-routers', 'GET', '/agents/{agent_id}/l3-routers/new', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'new')
('', 'PUT', '/agents/{agent_id}/l3-routers/:(id).:(format)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'update')
('', 'PUT', '/agents/{agent_id}/l3-routers/:(id)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'update')
('', 'DELETE', '/agents/{agent_id}/l3-routers/:(id).:(format)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'delete')
('', 'DELETE', '/agents/{agent_id}/l3-routers/:(id)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'delete')
('formatted_agent_edit_l3-routers', 'GET', '/agents/{agent_id}/l3-routers/:(id)/edit.:(format)', <wsgify at 96026320 wrapping <function resource at 0x5d30ed8>>, u'edit')
('', 'PUT', '/flavors/{flavor_id}/next_providers/:(id).:(format)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'update')
('', 'PUT', '/flavors/{flavor_id}/next_providers/:(id)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'update')('', 'DELETE', '/flavors/{flavor_id}/next_providers/:(id).:(format)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'delete')('', 'DELETE', '/flavors/{flavor_id}/next_providers/:(id)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'delete')
('formatted_flavor_edit_next_providers', 'GET', '/flavors/{flavor_id}/next_providers/:(id)/edit.:(format)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'edit')('flavor_edit_next_providers', 'GET', '/flavors/{flavor_id}/next_providers/:(id)/edit', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'edit')('formatted_flavor_next_providers', 'GET', '/flavors/{flavor_id}/next_providers/:(id).:(format)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'show')('flavor_next_providers', 'GET', '/flavors/{flavor_id}/next_providers/:(id)', <wsgify at 96042192 wrapping <function resource at 0x5d3b1b8>>, u'show')('', 'POST', '/flavors/{flavor_id}/service_profiles.:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'create')('', 'POST', '/flavors/{flavor_id}/service_profiles', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'create')
('formatted_flavor_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles.:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'index')('flavor_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'index')
('formatted_flavor_new_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles/new.:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'new')
('flavor_new_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles/new', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'new')
('', 'PUT', '/flavors/{flavor_id}/service_profiles/:(id).:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'update')
('', 'PUT', '/flavors/{flavor_id}/service_profiles/:(id)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'update')
('', 'DELETE', '/flavors/{flavor_id}/service_profiles/:(id).:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'delete')
('', 'DELETE', '/flavors/{flavor_id}/service_profiles/:(id)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'delete')
('formatted_flavor_edit_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles/:(id)/edit.:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'edit')
('flavor_edit_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles/:(id)/edit', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'edit')
('formatted_flavor_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles/:(id).:(format)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'show')
('flavor_service_profiles', 'GET', '/flavors/{flavor_id}/service_profiles/:(id)', <wsgify at 96042960 wrapping <function resource at 0x5d3b230>>, u'show')
('', 'POST', '/availability_zones.:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'create')
('', 'POST', '/availability_zones', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'create')
('formatted_availability_zones', 'GET', '/availability_zones.:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'index')
('availability_zones', 'GET', '/availability_zones', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'index')
('formatted_new_availability_zones', 'GET', '/availability_zones/new.:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'new')
('new_availability_zones', 'GET', '/availability_zones/new', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'new')
('', 'PUT', '/availability_zones/:(id).:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'update')
('', 'PUT', '/availability_zones/:(id)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'update')
('', 'DELETE', '/availability_zones/:(id).:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'delete')
('', 'DELETE', '/availability_zones/:(id)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'delete')
('formatted_edit_availability_zones', 'GET', '/availability_zones/:(id)/edit.:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'edit')
('edit_availability_zones', 'GET', '/availability_zones/:(id)/edit', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'edit')
('formatted_availability_zones', 'GET', '/availability_zones/:(id).:(format)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'show')
('availability_zones', 'GET', '/availability_zones/:(id)', <wsgify at 96052304 wrapping <function resource at 0x5d3b2a8>>, u'show')
('/quotas/tenant', 'GET', '/quotas/tenant', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'tenant')
('/quotas/tenant_format', 'GET', '/quotas/tenant.:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'tenant')
('', 'POST', '/quotas.:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'create')
('', 'POST', '/quotas', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'create')
('formatted_quotas', 'GET', '/quotas.:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'index')
('quotas', 'GET', '/quotas', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'index')
('formatted_new_quotas', 'GET', '/quotas/new.:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'new')
('new_quotas', 'GET', '/quotas/new', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'new')
('', 'PUT', '/quotas/:(id).:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'update')
('', 'PUT', '/quotas/:(id)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'update')
('', 'DELETE', '/quotas/:(id).:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'delete')
('', 'DELETE', '/quotas/:(id)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'delete')
('formatted_default_quotas', 'GET', '/quotas/:(id)/default.:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'default')
('default_quotas', 'GET', '/quotas/:(id)/default', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'default')
('formatted_edit_quotas', 'GET', '/quotas/:(id)/edit.:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'edit')
('edit_quotas', 'GET', '/quotas/:(id)/edit', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'edit')
('formatted_quotas', 'GET', '/quotas/:(id).:(format)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'show')
('quotas', 'GET', '/quotas/:(id)', <wsgify at 96052752 wrapping <function resource at 0x5d3b320>>, u'show')
('', 'POST', '/address-scopes.:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'create')
('', 'POST', '/address-scopes', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'create')
('formatted_address-scopes', 'GET', '/address-scopes.:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'index')
('address-scopes', 'GET', '/address-scopes', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'index')
('formatted_new_address-scopes', 'GET', '/address-scopes/new.:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'new')
('new_address-scopes', 'GET', '/address-scopes/new', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'new')
('', 'PUT', '/address-scopes/:(id).:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'update')
('', 'PUT', '/address-scopes/:(id)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'update')
('', 'DELETE', '/address-scopes/:(id).:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'delete')
('', 'DELETE', '/address-scopes/:(id)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'delete')
('formatted_edit_address-scopes', 'GET', '/address-scopes/:(id)/edit.:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'edit')
('edit_address-scopes', 'GET', '/address-scopes/:(id)/edit', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'edit')
('formatted_address-scopes', 'GET', '/address-scopes/:(id).:(format)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'show')
('address-scopes', 'GET', '/address-scopes/:(id)', <wsgify at 96053648 wrapping <function resource at 0x5d3b398>>, u'show')
('', 'POST', '/service-providers.:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'create')
('', 'POST', '/service-providers', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'create')
('formatted_service-providers', 'GET', '/service-providers.:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'index')
('service-providers', 'GET', '/service-providers', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'index')
('formatted_new_service-providers', 'GET', '/service-providers/new.:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'new')
('new_service-providers', 'GET', '/service-providers/new', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'new')
('', 'PUT', '/service-providers/:(id).:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'update')
('', 'PUT', '/service-providers/:(id)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'update')
('', 'DELETE', '/service-providers/:(id).:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'delete')
('', 'DELETE', '/service-providers/:(id)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'delete')
('formatted_edit_service-providers', 'GET', '/service-providers/:(id)/edit.:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'edit')
('edit_service-providers', 'GET', '/service-providers/:(id)/edit', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'edit')
('formatted_service-providers', 'GET', '/service-providers/:(id).:(format)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'show')
('service-providers', 'GET', '/service-providers/:(id)', <wsgify at 96054672 wrapping <function resource at 0x5d3b410>>, u'show')
('', 'POST', '/onosfp/flows.:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'create')
('', 'POST', '/onosfp/flows', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'create')
('formatted_flows', 'GET', '/onosfp/flows.:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'index')
('flows', 'GET', '/onosfp/flows', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'index')
('formatted_new_flows', 'GET', '/onosfp/flows/new.:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'new')
('new_flows', 'GET', '/onosfp/flows/new', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'new')
('', 'PUT', '/onosfp/flows/:(id).:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'update')
('', 'PUT', '/onosfp/flows/:(id)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'update')
('', 'DELETE', '/onosfp/flows/:(id).:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'delete')
('', 'DELETE', '/onosfp/flows/:(id)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'delete')
('formatted_edit_flows', 'GET', '/onosfp/flows/:(id)/edit.:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'edit')
('edit_flows', 'GET', '/onosfp/flows/:(id)/edit', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'edit')
('formatted_flows', 'GET', '/onosfp/flows/:(id).:(format)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'show')
('flows', 'GET', '/onosfp/flows/:(id)', <wsgify at 96055248 wrapping <function resource at 0x5d3b488>>, u'show')
('', 'POST', '/security-groups.:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'create')
('', 'POST', '/security-groups', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'create')
('formatted_security-groups', 'GET', '/security-groups.:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'index')
('security-groups', 'GET', '/security-groups', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'index')
('formatted_new_security-groups', 'GET', '/security-groups/new.:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'new')
('new_security-groups', 'GET', '/security-groups/new', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'new')
('', 'PUT', '/security-groups/:(id).:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'update')
('', 'PUT', '/security-groups/:(id)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'update')
('', 'DELETE', '/security-groups/:(id).:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'delete')
('', 'DELETE', '/security-groups/:(id)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'delete')
('formatted_edit_security-groups', 'GET', '/security-groups/:(id)/edit.:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'edit')
('edit_security-groups', 'GET', '/security-groups/:(id)/edit', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'edit')
('formatted_security-groups', 'GET', '/security-groups/:(id).:(format)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'show')
('security-groups', 'GET', '/security-groups/:(id)', <wsgify at 96072848 wrapping <function resource at 0x5d3b6e0>>, u'show')
('', 'POST', '/security-group-rules.:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'create')
('', 'POST', '/security-group-rules', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'create')
('formatted_security-group-rules', 'GET', '/security-group-rules.:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'index')
('security-group-rules', 'GET', '/security-group-rules', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'index')
('formatted_new_security-group-rules', 'GET', '/security-group-rules/new.:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'new')
('new_security-group-rules', 'GET', '/security-group-rules/new', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'new')
('', 'PUT', '/security-group-rules/:(id).:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'update')
('', 'PUT', '/security-group-rules/:(id)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'update')
('', 'DELETE', '/security-group-rules/:(id).:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'delete')
('', 'DELETE', '/security-group-rules/:(id)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'delete')
('formatted_edit_security-group-rules', 'GET', '/security-group-rules/:(id)/edit.:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'edit')
('edit_security-group-rules', 'GET', '/security-group-rules/:(id)/edit', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'edit')
('formatted_security-group-rules', 'GET', '/security-group-rules/:(id).:(format)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'show')
('security-group-rules', 'GET', '/security-group-rules/:(id)', <wsgify at 96074384 wrapping <function resource at 0x5d3b938>>, u'show')
('', 'DELETE', '/routers/:(id).:(format)', <wsgify at 93473616 wrapping <function resource at 0x5d3bcf8>>, u'delete')
('', 'DELETE', '/routers/:(id)', <wsgify at 93473616 wrapping <function resource at 0x5d3bcf8>>, u'delete')
('formatted_edit_routers', 'GET', '/routers/:(id)/edit.:(format)', <wsgify at 93473616 wrapping <function resource at 0x5d3bcf8>>, u'edit')
('edit_routers', 'GET', '/routers/:(id)/edit', <wsgify at 93473616 wrapping <function resource at 0x5d3bcf8>>, u'edit')
('formatted_routers', 'GET', '/routers/:(id).:(format)', <wsgify at 93473616 wrapping <function resource at 0x5d3bcf8>>, u'show')
('routers', 'GET', '/routers/:(id)', <wsgify at 93473616 wrapping <function resource at 0x5d3bcf8>>, u'show')
('', 'POST', '/floatingips.:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'create')
('', 'POST', '/floatingips', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'create')
('formatted_floatingips', 'GET', '/floatingips.:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'index')
('floatingips', 'GET', '/floatingips', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'index')
('formatted_new_floatingips', 'GET', '/floatingips/new.:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'new')
('new_floatingips', 'GET', '/floatingips/new', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'new')
('', 'PUT', '/floatingips/:(id).:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'update')
('', 'PUT', '/floatingips/:(id)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'update')
('', 'DELETE', '/floatingips/:(id).:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'delete')
('', 'DELETE', '/floatingips/:(id)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'delete')
('formatted_edit_floatingips', 'GET', '/floatingips/:(id)/edit.:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'edit')
('edit_floatingips', 'GET', '/floatingips/:(id)/edit', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'edit')
('formatted_floatingips', 'GET', '/floatingips/:(id).:(format)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'show')
('floatingips', 'GET', '/floatingips/:(id)', <wsgify at 88474960 wrapping <function resource at 0x5d3bf50>>, u'show')
```

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

*这里的 python 对象的 id 不一样，是因为中间重启了一次 neutron。*

## controller 的实现

* 那么下面我们就跟踪一下 controller 的调用，我们找一个 extension 的实例（例如 `Availability_zone`），我么就可以发现实现 controller 的是 `neutron.api.v2.resource.Resource` 方法：

*`Resource` 是个方法，不是类，这个方法返回了一个可以处理 wsgi 消息的方法 `resource`。*


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