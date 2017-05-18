# neutron 中资源请求的属性检查

若针对 neutron 中某一资源的进行某种方法的请求时需要传递一定的数据（request.body），则会对数据中包含的资源属性进行检查。

这些方法都是在 *neutron/api/v2/attributes.py* 中实现。

## 数据库字段

```
NAME_MAX_LEN = 255
TENANT_ID_MAX_LEN = 255
DESCRIPTION_MAX_LEN = 255
LONG_DESCRIPTION_MAX_LEN = 1024
DEVICE_ID_MAX_LEN = 255
DEVICE_OWNER_MAX_LEN = 255
```

## `_lib(old_name)`

* 有些方法已经从 neutron 中迁移到了 neutron-lib 中，`_lib`就是做这个映射的。

## `RESOURCE_ATTRIBUTE_MAP`

定义资源集合的属性信息。

这些信息可能在 service plugin 和 extension 中被更新。

所有的检查都是基于这个字典来做的。

## `PLURALS`

资源集合名称与资源名称的映射

## `get_collection_info`

从 `RESOURCE_ATTRIBUTE_MAP` 获取资源集合的属性信息

## `get_resource_info`

从 `RESOURCE_ATTRIBUTE_MAP` 获取资源的属性信息

## populate_project_info

```
def populate_project_info(attributes):
"""
Ensure that both project_id and tenant_id attributes are present.

If either project_id or tenant_id is present in attributes then ensure
that both are present.

If neither are present then attributes is not updated.

:param attributes: a dictionary of resource/API attributes
:type attributes: dict

:return: the updated attributes dictionary
:rtype: dict
"""
if 'tenant_id' in attributes and 'project_id' not in attributes:
# TODO(HenryG): emit a deprecation warning here
attributes['project_id'] = attributes['tenant_id']
elif 'project_id' in attributes and 'tenant_id' not in attributes:
# Backward compatibility for code still using tenant_id
attributes['tenant_id'] = attributes['project_id']

if attributes.get('project_id') != attributes.get('tenant_id'):
msg = _("'project_id' and 'tenant_id' do not match")
raise webob.exc.HTTPBadRequest(msg)

return attributes
```

1. 若是 attributes 中含有 `tenant_id` 或者 `project_id` 中的任何一个，则将另一个设置为与之相等（更新 attributes）；
2. 若是 attributes 中同时含有 `tenant_id` 和 `project_id`，则判断其是否相等，不相等则引发异常
3. 其他情况则不更新 attributes

## `_validate_privileges`

```
def _validate_privileges(context, res_dict):
if ('project_id' in res_dict and
res_dict['project_id'] != context.project_id and
not context.is_admin):
msg = _("Specifying 'project_id' or 'tenant_id' other than "
"authenticated project in request requires admin privileges")
raise webob.exc.HTTPBadRequest(msg)
```

若消息体（request.body）中的传递过来的资源属性（res_dict）包含有 `project_id`，则检查其是否和消息体传递过来的 context 中的 `project_id` 一致。

若不一致，且不为 admin，则引发异常

## `populate_tenant_id`

```
def populate_tenant_id(context, res_dict, attr_info, is_create):
populate_project_info(res_dict)
_validate_privileges(context, res_dict)

if is_create and 'project_id' not in res_dict:
if context.project_id:
res_dict['project_id'] = context.project_id

# For backward compatibility
res_dict['tenant_id'] = context.project_id

elif 'tenant_id' in attr_info:
msg = _("Running without keystone AuthN requires "
"that tenant_id is specified")
raise webob.exc.HTTPBadRequest(msg)
```

* 调用 `populate_project_info` 和 `_validate_privileges` 方法

* 在调用的为 create 方法（is_create 为真，请求方法为 POST），且消息体（request.body）中的传递过来的资源属性（res_dict，已经过前面的方法升级）不包含有 `project_id`的情况下：
1. 若认证的上下文中包含 `project_id` 属性，则将其填充到传递过来的资源属性中
2. 若认证的上下文中不包含 `project_id` 属性，但是资源的属性列表 `attr_info` 要求 `tenant_id`，则引发异常

## verify_attributes

```
def verify_attributes(res_dict, attr_info):
populate_project_info(attr_info)

extra_keys = set(res_dict.keys()) - set(attr_info.keys())
if extra_keys:
msg = _("Unrecognized attribute(s) '%s'") % ', '.join(extra_keys)
raise webob.exc.HTTPBadRequest(msg)
```

* 检查经过填充后的资源请求数据 `res_dict` 是否比资源本身的属性消息 `attr_info` 要多，若是多的话则引发异常

##

```
def fill_default_value(attr_info, res_dict,
exc_cls=ValueError,
check_allow_post=True):
for attr, attr_vals in six.iteritems(attr_info):
if attr_vals['allow_post']:
if 'default' not in attr_vals and attr not in res_dict:
msg = _("Failed to parse request. Required "
"attribute '%s' not specified") % attr
raise exc_cls(msg)
res_dict[attr] = res_dict.get(attr,
attr_vals.get('default'))
elif check_allow_post:
if attr in res_dict:
msg = _("Attribute '%s' not allowed in POST") % attr
raise exc_cls(msg)
```

检查资源本身的属性信息中是否有的属性可以在 POST 类型的请求方法中使用：

1. 若可以则，检查资源请求的数据是否包含了资源的原本的所有属性，若没有且该属性有默认值，则将其更新到请求数据中，若没有默认值则引发异常；
2. 若不可以，但是该资源属性在 POST 方法类型的请求中，则引发异常；

## 测试

```
neutron net-create ext-net --router:external True --provider:physical_network external --provider:network_type flat
```

* gdb 调试打印信息：

```
(Pdb) request.body
'{"network": {"router:external": "True", "provider:network_type": "flat", "name": "ext-net", "provider:physical_network": "external", "admin_state_up": true}}'

(Pdb) p args['body']
{u'network': {u'router:external': u'True', u'admin_state_up': True, u'name': u'ext-net', u'provider:physical_network': u'external', u'provider:network_type': u'flat'}}
```

其中：request.body为命令传递过来的数据；args['body']为解析后的数据，这个是要传递给 controller 中 create（测试命令使用的 create 方法） 方法的。