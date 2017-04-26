# extension 架构



## 基类 `class ExtensionDescriptor(object)`

* 基类代码：

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

单看一个抽象类没啥好看的，我们结合一个具体的实现来看：[availability_zone extension](https://github.com/openstack/neutron/blob/stable/newton/neutron/extensions/availability_zone.py)

1. `ExtensionDescriptor` 是个抽象类（`@six.add_metaclass(abc.ABCMeta)`），定义了 extension 的基本框架；

2. `get_name` 抽象方法，返回 extension 的名字；

3. `get_alias` 抽象方法，返回 extension 的别名；

4. `get_description` 抽象方法，返回 extension 的描述；

5. `get_updated` 抽象方法，返回该 extension 最后更新的时间戳；

6. `get_resources` 

### 测试

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

## 参考

[API Extensions](https://wiki.openstack.org/wiki/NeutronDevelopment#API_Extensions)

[JUNO NEUTRON中的plugin和extension介绍及加载机制](http://bingotree.cn/?p=660&utm_source=tuicool&utm_medium=referral)

































  