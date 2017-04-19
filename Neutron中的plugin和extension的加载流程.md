# Neutron 中 plugin 和 extension 的加载流程

主要参考：[JUNO NEUTRON中的plugin和extension介绍及加载机制](http://bingotree.cn/?p=660&utm_source=tuicool&utm_medium=referral)

## 预备知识

* wsgi

 * 请参考我收集的关于 wsgi 的资料

* neutron_lib

* oslo_service

* stevedore

 *  [Python深入：stevedore简介](http://blog.csdn.net/gqtcgq/article/details/49620279)
 * [stevedore – Manage Dynamic Plugins for Python Applications](https://docs.openstack.org/developer/stevedore/)  

* python 模块

 * weakref
 * six
 * collections

## 加载 plugin

*newton 版本中的 plugin 的加载流程，与参考文章中写的变化不大，我这里只说一下不同的地方。*

### `_get_plugin_instance`

**作用：** 加载 plugin 的实例

```
@staticmethod
def load_class_for_provider(namespace, plugin_provider):
    """Loads plugin using alias or class name
    :param namespace: namespace where alias is defined
    :param plugin_provider: plugin alias or class name
    :returns plugin that is loaded
    :raises ImportError if fails to load plugin
    """

    try:
        return utils.load_class_by_alias_or_classname(namespace,
                plugin_provider)
    except ImportError:
        with excutils.save_and_reraise_exception():
            LOG.error(_LE("Plugin '%s' not found."), plugin_provider)

def _get_plugin_instance(self, namespace, plugin_provider):
    plugin_class = self.load_class_for_provider(namespace, plugin_provider)
    return plugin_class()
```

从代码可以看出实际 plugin 的加载功能已经被抽象出来，演变成了一个通用的功能，即根据提供的 `namespace` 和 `name` 加载指定的类或者方法：

```
def load_class_by_alias_or_classname(namespace, name):
    """Load class using stevedore alias or the class name
    :param namespace: namespace where the alias is defined
    :param name: alias or class name of the class to be loaded
    :returns class if calls can be loaded
    :raises ImportError if class cannot be loaded
    """

    if not name:
        LOG.error(_LE("Alias or class name is not set"))
        raise ImportError(_("Class not found."))
    try:
        # Try to resolve class by alias
        mgr = _SilentDriverManager(namespace, name)
        class_to_load = mgr.driver
    except RuntimeError:
        e1_info = sys.exc_info()
        # Fallback to class name
        try:
            class_to_load = importutils.import_class(name)
        except (ImportError, ValueError):
            LOG.error(_LE("Error loading class by alias"),
                      exc_info=e1_info)
            LOG.error(_LE("Error loading class by class name"),
                      exc_info=True)
            raise ImportError(_("Class not found."))
    return class_to_load
```

`load_class_by_alias_or_classname` 参数中的 `name` 既可以是 `alias/entry_points` 也可以是一个具体的可加载的类/方法名。

### neutron.plugins.common.constants.py

*该模块定义了 Neutron 中常用的一些常量。*

## `_load_service_plugins`

**作用：** 加载 service plugins

```
def _load_services_from_core_plugin(self):
    """Puts core plugin in service_plugins for supported services."""
    LOG.debug("Loading services supported by the core plugin")

    # supported service types are derived from supported extensions
    for ext_alias in getattr(self.plugin,
                             "supported_extension_aliases", []):
        if ext_alias in constants.EXT_TO_SERVICE_MAPPING:
            service_type = constants.EXT_TO_SERVICE_MAPPING[ext_alias]
            self.service_plugins[service_type] = self.plugin
            LOG.info(_LI("Service %s is supported by the core plugin"),
                     service_type)

def _get_default_service_plugins(self):
    """Get default service plugins to be loaded."""
    return constants.DEFAULT_SERVICE_PLUGINS.keys()

def _load_service_plugins(self):
    """Loads service plugins.

    Starts from the core plugin and checks if it supports
    advanced services then loads classes provided in configuration.
    """
    # load services from the core plugin first
    self._load_services_from_core_plugin()

    plugin_providers = cfg.CONF.service_plugins
    plugin_providers.extend(self._get_default_service_plugins())
    LOG.debug("Loading service plugins: %s", plugin_providers)
    for provider in plugin_providers:
        if provider == '':
            continue

        LOG.info(_LI("Loading Plugin: %s"), provider)
        plugin_inst = self._get_plugin_instance('neutron.service_plugins',
                                                provider)

        # only one implementation of svc_type allowed
        # specifying more than one plugin
        # for the same type is a fatal exception
        if plugin_inst.get_plugin_type() in self.service_plugins:
            raise ValueError(_("Multiple plugins for service "
                               "%s were configured") %
                             plugin_inst.get_plugin_type())

        self.service_plugins[plugin_inst.get_plugin_type()] = plugin_inst

        # search for possible agent notifiers declared in service plugin
        # (needed by agent management extension)
        if (hasattr(self.plugin, 'agent_notifiers') and
                hasattr(plugin_inst, 'agent_notifiers')):
            self.plugin.agent_notifiers.update(plugin_inst.agent_notifiers)

        LOG.debug("Successfully loaded %(type)s plugin. "
                  "Description: %(desc)s",
                  {"type": plugin_inst.get_plugin_type(),
                   "desc": plugin_inst.get_plugin_description()})
```

* `_load_services_from_core_plugin` 加载 core plugin 提供的服务

* `_get_default_service_plugins` 获取默认的 service plugins的扩展别名，进而可获取其对应的 entry point

* 还是通过 `_get_plugin_instance` 方法来加载所有的 service plugin 的实例

**不管是 core plugin 还是 service plugin 都是放在 `self.service_plugins` 中进行管理的。**


## 加载 extension

### `get_extensions_path` 

**作用：** 从配置文件以及 `neutron.extensions.__patch__` 中加载 extensions 的路径

```
# Returns the extension paths from a config entry and the __path__
# of neutron.extensions
def get_extensions_path(service_plugins=None):
    paths = collections.OrderedDict()

    # Add Neutron core extensions
    paths[neutron.extensions.__path__[0]] = 1
    if service_plugins:
        # Add Neutron *-aas extensions
        for plugin in service_plugins.values():
            neutron_mod = provider_configuration.NeutronModule(
                plugin.__module__.split('.')[0])
            try:
                paths[neutron_mod.module().extensions.__path__[0]] = 1
            except AttributeError:
                # Occurs normally if module has no extensions sub-module
                pass

    # Add external/other plugins extensions
    if cfg.CONF.api_extensions_path:
        for path in cfg.CONF.api_extensions_path.split(":"):
            paths[path] = 1

    LOG.debug("get_extension_paths = %s", paths)

    # Re-build the extension string
    path = ':'.join(paths)
    return path
```

* 以 plugin 为模块，加载该 plugin 所在包中的 extensions 模块的路径。

*为什么要这么做呢，因为有人可能以一个单独的包来实现一个 plugin*

* 加载配置文件中声明的 api_extensions_path

* `NeutronModule` 待研究
 
* 返回一个以 `:` 分割的路径字符串