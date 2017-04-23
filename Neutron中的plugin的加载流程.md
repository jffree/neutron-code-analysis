# Neutron 中的 plugin 的加载

```
plugin = manager.NeutronManager.get_plugin()
```

```python
@six.add_metaclass(profiler.TracedMeta)
class NeutronManager(object):

...

    @classmethod
    @utils.synchronized("manager")
    def _create_instance(cls):
        if not cls.has_instance():
            cls._instance = cls()

    @classmethod
    def has_instance(cls):
        return cls._instance is not None

    @classmethod
    def clear_instance(cls):
        cls._instance = None

    @classmethod
    def get_instance(cls):
        # double checked locking
        if not cls.has_instance():
            cls._create_instance()
        return cls._instance

    @classmethod
    def get_plugin(cls):
        # Return a weakref to minimize gc-preventing references.
        return weakref.proxy(cls.get_instance().plugin)
```

*从上面的代码看出，一切都要去 `NeutronManager` 的初始化函数中找答案。*

## `NeutronManager` 的初始化

```
@six.add_metaclass(profiler.TracedMeta)
class NeutronManager(object):
    """Neutron's Manager class.

    Neutron's Manager class is responsible for parsing a config file and
    instantiating the correct plugin that concretely implements
    neutron_plugin_base class.
    The caller should make sure that NeutronManager is a singleton.
    """
    _instance = None
    __trace_args__ = {"name": "rpc"}

    def __init__(self, options=None, config_file=None):
        # If no options have been provided, create an empty dict
        if not options:
            options = {}

        msg = validate_pre_plugin_load()
        if msg:
            LOG.critical(msg)
            raise Exception(msg)

        # NOTE(jkoelker) Testing for the subclass with the __subclasshook__
        #                breaks tach monitoring. It has been removed
        #                intentionally to allow v2 plugins to be monitored
        #                for performance metrics.
        plugin_provider = cfg.CONF.core_plugin
        LOG.info(_LI("Loading core plugin: %s"), plugin_provider)
        self.plugin = self._get_plugin_instance(CORE_PLUGINS_NAMESPACE,
                                                plugin_provider)
        msg = validate_post_plugin_load()
        if msg:
            LOG.critical(msg)
            raise Exception(msg)

        # core plugin as a part of plugin collection simplifies
        # checking extensions
        # TODO(enikanorov): make core plugin the same as
        # the rest of service plugins
        self.service_plugins = {constants.CORE: self.plugin}
        self._load_service_plugins()
        # Used by pecan WSGI
        self.resource_plugin_mappings = {}
        self.resource_controller_mappings = {}
        self.path_prefix_resource_mappings = defaultdict(list)
```

* 初始化函数中完成了对 plugin 的加载，下面我们分析是如何实现的。

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

### `neutron.plugins.common.constants.py`

*该模块定义了 Neutron 中常用的一些常量。*

### `_load_service_plugins`

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

**不管是 core plugin 还是 service plugin 都是放在 `self.service_plugins` 中进行管理的。但是 core plugin 还是被特殊对待了一下，它同时也被存放于 `self.plugin`中了。那么我们本文中的第一行代码在加载了所有的 plugin 的同时，还获取了 core plugin 的实例。**