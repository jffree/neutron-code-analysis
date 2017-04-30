# extension 架构

extension 为 neutron plugin 的向外提供接口。根据 rest api，extension 向外暴露的是资源、操作资源的方法以及操作资源的参数。那么 extension 就分为三种：

1. 直接实现了某种新的resource。比如实现了资源XXX，那么我可以通过/v2.0/XXX进行XXX资源的操作。这个是最类似于实现一个新的service\_plugin的

2. 对现有的某种资源添加某种操作功能。比如对于ports资源，我想有一个动作是做绑定（打个比方，不一定确切），则可以通过extension在现有的plugin基础上增加功能，比如对/v2.0/ports增加/action接口

3. 对现有的某个REST API请求增加参数。比如对于/v2.0/ports我本来创建的时候什么参数都不用提供，现在我希望POST请求能带上参数NAME，则可以通过extension来实现

## extension 的实现步骤：

1. 在 _neutron/extensions_ 文件夹下创建一个模块

2. 在这个模块中创建一个与模块名一致的，继承于 `ExtensionDescriptor` 的类，这就是你的 extension

3. 实现 extension 的基本方法和相应功能

4. 通过 plugin 的 `supported_extension_aliases` 将 extension 与 plugin 关联起来

## 抽象类 `class ExtensionDescriptor(object)`

* 代码：

```
@six.add_metaclass(abc.ABCMeta)
class ExtensionDescriptor(object):
    """Base class that defines the contract for extensions."""

    @abc.abstractmethod
    def get_name(self):
        """The name of the extension.

        e.g. 'Fox In Socks'
        """

    @abc.abstractmethod
    def get_alias(self):
        """The alias for the extension.

        e.g. 'FOXNSOX'
        """

    @abc.abstractmethod
    def get_description(self):
        """Friendly description for the extension.

        e.g. 'The Fox In Socks Extension'
        """

    @abc.abstractmethod
    def get_updated(self):
        """The timestamp when the extension was last updated.

        e.g. '2011-01-22T13:25:27-06:00'
        """
        # NOTE(justinsb): Not sure of the purpose of this is, vs the XML NS

    def get_resources(self):
        """List of extensions.ResourceExtension extension objects.

        Resources define new nouns, and are accessible through URLs.
        """
        resources = []
        return resources

    def get_actions(self):
        """List of extensions.ActionExtension extension objects.

        Actions are verbs callable from the API.
        """
        actions = []
        return actions

    def get_request_extensions(self):
        """List of extensions.RequestException extension objects.

        Request extensions are used to handle custom request data.
        """
        request_exts = []
        return request_exts

    def get_extended_resources(self, version):
        """Retrieve extended resources or attributes for core resources.

        Extended attributes are implemented by a core plugin similarly
        to the attributes defined in the core, and can appear in
        request and response messages. Their names are scoped with the
        extension's prefix. The core API version is passed to this
        function, which must return a
        map[<resource_name>][<attribute_name>][<attribute_property>]
        specifying the extended resource attribute properties required
        by that API version.

        Extension can add resources and their attr definitions too.
        The returned map can be integrated into RESOURCE_ATTRIBUTE_MAP.
        """
        return {}

    def get_plugin_interface(self):
        """Returns an abstract class which defines contract for the plugin.

        The abstract class should inherit from extensions.PluginInterface,
        Methods in this abstract class  should be decorated as abstractmethod
        """
        return None

    def get_required_extensions(self):
        """Returns a list of extensions to be processed before this one."""
        return []

    def get_optional_extensions(self):
        """Returns a list of extensions to be processed before this one.

        Unlike get_required_extensions. This will not fail the loading of
        the extension if one of these extensions is not present. This is
        useful for an extension that extends multiple resources across
        other extensions that should still work for the remaining extensions
        when one is missing.
        """
        return []

    def update_attributes_map(self, extended_attributes,
                              extension_attrs_map=None):
        """Update attributes map for this extension.

        This is default method for extending an extension's attributes map.
        An extension can use this method and supplying its own resource
        attribute map in extension_attrs_map argument to extend all its
        attributes that needs to be extended.

        If an extension does not implement update_attributes_map, the method
        does nothing and just return.
        """
        if not extension_attrs_map:
            return

        for resource, attrs in six.iteritems(extension_attrs_map):
            extended_attrs = extended_attributes.get(resource)
            if extended_attrs:
                attrs.update(extended_attrs)

    def get_pecan_resources(self):
        """List of PecanResourceExtension extension objects.

        Resources define new nouns, and are accessible through URLs.
        The controllers associated with each instance of
        extensions.ResourceExtension should be a subclass of
        neutron.pecan_wsgi.controllers.utils.NeutronPecanController.

        If a resource is defined in both get_resources and get_pecan_resources,
        the resource defined in get_pecan_resources will take precedence.
        """
        return []
```

### 分析

1. `ExtensionDescriptor` 是个抽象类（`@six.add_metaclass(abc.ABCMeta)`），定义了 extension 的基本框架；

2. `get_name` 抽象方法，返回 extension 的名字；

3. `get_alias` 抽象方法，返回 extension 的别名；

4. `get_description` 抽象方法，返回 extension 的描述；

5. `get_updated` 抽象方法，返回该 extension 最后更新的时间戳；

6. `get_resources` 返回一个以 `extensions.ResourceExtension` 封装的资源列表。我们上面说了 extension 分为三类，那么第一类（暴露资源的 extension）必须实现这个方法。

7. `get_actions` 返回一个以 `extensions.ActionExtension` 封装的列表。这个是 第二类 extension（暴露动作）必须实现的方法。

8. `get_request_extensions` 返回一个以 `extensions.RequestException` 封装的列表。这个是第三类 extension（暴露参数）必须实现的方法。

9. `get_extended_resources`，若是这个 extension 向外暴露了资源，那么这个 extension 所暴露的资源以及资源的属性就会通过这个方法获得。

10. `get_plugin_interface` 返回一个从 `extension.PluginInterface` 继承的抽象类，这个抽象类中的方法应该被装饰为 `abstractmethod`。

### 测试

单看一个抽象类没啥好看的，我们结合一个具体的实现来看：[availability\_zone extension](https://github.com/openstack/neutron/blob/stable/newton/neutron/extensions/availability_zone.py)

#### availability\_zone extension 中的公共属性和方法

```
AZ_HINTS_DB_LEN = 255


# resource independent common methods
def convert_az_list_to_string(az_list):
    return jsonutils.dumps(az_list)


def convert_az_string_to_list(az_string):
    return jsonutils.loads(az_string) if az_string else []


def _validate_availability_zone_hints(data, valid_value=None):
    # syntax check only here. existence of az will be checked later.
    msg = validators.validate_list_of_unique_strings(data)
    if msg:
        return msg
    az_string = convert_az_list_to_string(data)
    if len(az_string) > AZ_HINTS_DB_LEN:
        msg = _("Too many availability_zone_hints specified")
        raise exceptions.InvalidInput(error_message=msg)

validators.add_validator('availability_zone_hints',
                         _validate_availability_zone_hints)

# Attribute Map
RESOURCE_NAME = 'availability_zone'
AVAILABILITY_ZONES = 'availability_zones'
AZ_HINTS = 'availability_zone_hints'
# name: name of availability zone (string)
# resource: type of resource: 'network' or 'router'
# state: state of availability zone: 'available' or 'unavailable'
# It means whether users can use the availability zone.
RESOURCE_ATTRIBUTE_MAP = {
    AVAILABILITY_ZONES: {
        'name': {'is_visible': True},
        'resource': {'is_visible': True},
        'state': {'is_visible': True}
    }
}

EXTENDED_ATTRIBUTES_2_0 = {
    'agents': {
        RESOURCE_NAME: {'allow_post': False, 'allow_put': False,
                        'is_visible': True}
    }
}


class AvailabilityZoneNotFound(exceptions.NotFound):
    message = _("AvailabilityZone %(availability_zone)s could not be found.")
```

#### `ExtensionDescriptor`中的四个抽象方法实例：

```
class Availability_zone(extensions.ExtensionDescriptor):
    """Availability zone extension."""

    @classmethod
    def get_name(cls):
        return "Availability Zone"

    @classmethod
    def get_alias(cls):
        return "availability_zone"

    @classmethod
    def get_description(cls):
        return "The availability zone extension."

    @classmethod
    def get_updated(cls):
        return "2015-01-01T10:00:00-00:00"
```

* 关于 `ExtensionDescriptor`中的四个抽象方法，其实是对该 extension 的简单描述，下面我们通过 `curl` 对 `Availability_zone` extension 进行测试：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/extensions/network_availability_zone -H 'Content-Type: application/json' -H 'X-Auth-Token: d25873d674ad42b7aefce8dad58b4763' | jq
```

返回值如下：

```
{
  "extension": {
    "alias": "network_availability_zone",
    "updated": "2015-01-01T10:00:00-00:00",
    "name": "Network Availability Zone",
    "links": [],
    "description": "Availability zone support for network."
  }
}
```

#### `get_resources` 方法实例：

```
    @classmethod
    def get_resources(cls):
        """Returns Ext Resources."""
        my_plurals = [(key, key[:-1]) for key in RESOURCE_ATTRIBUTE_MAP.keys()]
        attr.PLURALS.update(dict(my_plurals))
        plugin = manager.NeutronManager.get_plugin()
        params = RESOURCE_ATTRIBUTE_MAP.get(AVAILABILITY_ZONES)
        controller = base.create_resource(AVAILABILITY_ZONES,
                                          RESOURCE_NAME, plugin, params)

        ex = extensions.ResourceExtension(AVAILABILITY_ZONES, controller)

        return [ex]
```

`neutron.api.v2.base.Controller` 以及 `neutron.api.extensions.ResourceExtension` 是用于 resource wsgi 映射的实现，我们有专门的一节来讲解，这里我们只看一下 availability_zone extension 中 `get_resource` 方法的实现逻辑。

* 定义资源的复数名及单数名映射 `my_plurals`：`[('availability_zones', 'availability_zone')]`

* 更新 `neutron.api.v2.attributes.PLURALS` 属性，我们看一下这个变量：

```
# Store plural/singular mappings
PLURALS = {NETWORKS: NETWORK,
           PORTS: PORT,
           SUBNETS: SUBNET,
           SUBNETPOOLS: SUBNETPOOL,
           'dns_nameservers': 'dns_nameserver',
           'host_routes': 'host_route',
           'allocation_pools': 'allocation_pool',
           'fixed_ips': 'fixed_ip',
           'extensions': 'extension'}
```

那么我们更新后会变为：

```
# Store plural/singular mappings
PLURALS = {NETWORKS: NETWORK,
           PORTS: PORT,
           SUBNETS: SUBNET,
           SUBNETPOOLS: SUBNETPOOL,
           'dns_nameservers': 'dns_nameserver',
           'host_routes': 'host_route',
           'allocation_pools': 'allocation_pool',
           'fixed_ips': 'fixed_ip',
           'extensions': 'extension',
           'availability_zones':  'availability_zone'}
```

* 获取支持此 extension 的 plugin

#### `get_extended_resources` 方法实例：

```
    def get_extended_resources(self, version):
        if version == "2.0":
            return dict(list(EXTENDED_ATTRIBUTES_2_0.items()) +
                        list(RESOURCE_ATTRIBUTE_MAP.items()))
        else:
            return {}
```

返回值为：

```
{'availability_zones': {'state': {'is_visible': True}, 'resource': {'is_visible': True}, 'name': {'is_visible': True}}, 'agents': {'availability_zone': {'is_visible': True, 'allow_put': False, 'allow_post': False}}}
```

#### `get_plugin_interface`

## 参考

[API Extensions](https://wiki.openstack.org/wiki/NeutronDevelopment#API_Extensions)

[JUNO NEUTRON中的plugin和extension介绍及加载机制](http://bingotree.cn/?p=660&utm_source=tuicool&utm_medium=referral)

