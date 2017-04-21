# Neutron 中 plugin 和 extension 的加载流程

主要参考：[JUNO NEUTRON中的plugin和extension介绍及加载机制](http://bingotree.cn/?p=660&utm_source=tuicool&utm_medium=referral)

[neutron-server的启动流程(二)](http://blog.csdn.net/gj19890923/article/details/51345576)

*newton 版本中的 plugin 的加载流程，与参考文章中写的变化不大，我这里只说一下不同的地方。*

## 加载 plugin

```
plugin = manager.NeutronManager.get_plugin()
```

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

**不管是 core plugin 还是 service plugin 都是放在 `self.service_plugins` 中进行管理的。**


## 加载 extension

```
ext_mgr = extensions.PluginAwareExtensionManager.get_instance()
```

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

### `_load_all_extensions_from_path`

```
def _load_all_extensions_from_path(self, path):
    # Sorting the extension list makes the order in which they
    # are loaded predictable across a cluster of load-balanced
    # Neutron Servers
    for f in sorted(os.listdir(path)):
        try:
            LOG.debug('Loading extension file: %s', f)
            mod_name, file_ext = os.path.splitext(os.path.split(f)[-1])
            ext_path = os.path.join(path, f)
            if file_ext.lower() == '.py' and not mod_name.startswith('_'):
                mod = imp.load_source(mod_name, ext_path)
                ext_name = mod_name[0].upper() + mod_name[1:]
                new_ext_class = getattr(mod, ext_name, None)
                if not new_ext_class:
                    LOG.warning(_LW('Did not find expected name '
                                    '"%(ext_name)s" in %(file)s'),
                                {'ext_name': ext_name,
                                 'file': ext_path})
                    continue
                new_ext = new_ext_class()
                self.add_extension(new_ext)
        except Exception as exception:
            LOG.warning(_LW("Extension file %(f)s wasn't loaded due to "
                            "%(exception)s"),
                        {'f': f, 'exception': exception})
```

**在这个方法中我们可以看出 extension 方法的写法，就是一个 extension 模块（.py）里面必须有一个和这个模块名称一样，且首字母大写的类。**


*`add_extension` 方法是在父类 `ExtensionManager`*
```
def add_extension(self, ext):
    # Do nothing if the extension doesn't check out
    if not self._check_extension(ext):
        return

    alias = ext.get_alias()
    LOG.info(_LI('Loaded extension: %s'), alias)

    if alias in self.extensions:
        raise exceptions.DuplicatedExtension(alias=alias)
    self.extensions[alias] = ext

```

*子类 `PluginAwareExtensionManager` 中重写了 `_check_extension` 方法。*
```
def _check_extension(self, extension):
    """Check if an extension is supported by any plugin."""
    extension_is_valid = super(PluginAwareExtensionManager,
                               self)._check_extension(extension)
    if not extension_is_valid:
        return False

    alias = extension.get_alias()
    if alias in EXTENSION_SUPPORTED_CHECK_MAP:
        return EXTENSION_SUPPORTED_CHECK_MAP[alias]()

    return (self._plugins_support(extension) and
            self._plugins_implement_interface(extension))
```

```
def _plugins_support(self, extension):
    alias = extension.get_alias()
    supports_extension = alias in self.get_supported_extension_aliases()
    if not supports_extension:
        LOG.warning(_LW("Extension %s not supported by any of loaded "
                        "plugins"),
                    alias)
    return supports_extension

def get_plugin_supported_extension_aliases(self, plugin):
    """Return extension aliases supported by a given plugin"""
    aliases = set()
    # we also check all classes that the plugins inherit to see if they
    # directly provide support for an extension
    for item in [plugin] + plugin.__class__.mro():
        try:
            aliases |= set(
                getattr(item, "supported_extension_aliases", []))
        except TypeError:
            # we land here if a class has a @property decorator for
            # supported extension aliases. They only work on objects.
            pass
    return aliases
```

```
def _plugins_implement_interface(self, extension):
    if extension.get_plugin_interface() is None:
        return True
    for plugin in self.plugins.values():
        if isinstance(plugin, extension.get_plugin_interface()):
            return True
    LOG.warning(_LW("Loaded plugins do not implement extension "
                    "%s interface"),
                extension.get_alias())
    return False
```

```
def check_if_plugin_extensions_loaded(self):
    """Check if an extension supported by a plugin has been loaded."""
    plugin_extensions = self.get_supported_extension_aliases()
    missing_aliases = plugin_extensions - set(self.extensions)
    missing_aliases -= _PLUGIN_AGNOSTIC_EXTENSIONS
    if missing_aliases:
        raise exceptions.ExtensionsNotFound(
            extensions=list(missing_aliases))
```

我们一步步的追踪下来，可以发现这些信息：

1. `get_plugin_supported_extension_aliases` 方法搜集所有被加载的 plugin 支持的 extension (`supported_extension_aliases`)，返回支持的所有被支持的 extension 的 alias 的集合

2. `_plugins_implement_interface` 方法检查 extension 是否重写了 `get_plugin_interface` 方法，若是重写了该方法，则要求其返回值是 plugins 中一个的实例。

3. 将通过检查的 extension 存于 `self.extensions` 的字典（`{alias:实例}`）中。

4. 通过 `check_if_plugin_extensions_loaded` 函数检查是否所有的被 plugin 所支持 extension 都已经被加载。

## 加载所有的 resource

```
ext_mgr.extend_resources("2.0", attributes.RESOURCE_ATTRIBUTE_MAP)
```

### `extend_resources(self, version, attr_map)`

**作用：**在已有的资源（通过 rest api 访问的即为资源）的基础上扩展资源或者资源的属性

```
def extend_resources(self, version, attr_map):
    """Extend resources with additional resources or attributes.

    :param attr_map: the existing mapping from resource name to
    attrs definition.

    After this function, we will extend the attr_map if an extension
    wants to extend this map.
    """
    processed_exts = {}
    exts_to_process = self.extensions.copy()
    check_optionals = True
    # Iterate until there are unprocessed extensions or if no progress
    # is made in a whole iteration
    while exts_to_process:
        processed_ext_count = len(processed_exts)
        for ext_name, ext in list(exts_to_process.items()):
            # Process extension only if all required extensions
            # have been processed already
            required_exts_set = set(ext.get_required_extensions())
            if required_exts_set - set(processed_exts):
                continue
            optional_exts_set = set(ext.get_optional_extensions())
            if check_optionals and optional_exts_set - set(processed_exts):
                continue
            extended_attrs = ext.get_extended_resources(version)
            for res, resource_attrs in six.iteritems(extended_attrs):
                attr_map.setdefault(res, {}).update(resource_attrs)
            processed_exts[ext_name] = ext
            del exts_to_process[ext_name]
        if len(processed_exts) == processed_ext_count:
            # if we hit here, it means there are unsatisfied
            # dependencies. try again without optionals since optionals
            # are only necessary to set order if they are present.
            if check_optionals:
                check_optionals = False
                continue
            # Exit loop as no progress was made
            break
    if exts_to_process:
        unloadable_extensions = set(exts_to_process.keys())
        LOG.error(_LE("Unable to process extensions (%s) because "
                      "the configured plugins do not satisfy "
                      "their requirements. Some features will not "
                      "work as expected."),
                  ', '.join(unloadable_extensions))
        self._check_faulty_extensions(unloadable_extensions)
    # Extending extensions' attributes map.
    for ext in processed_exts.values():
        ext.update_attributes_map(attr_map)
```

* 从代码中可以看出，每一个 extension 都可能会有下面这三个方法： `get_required_extensions`、`get_optional_extensions`、`get_extended_resources`

* `get_required_extensions` 意味着加载 这个 extension 的 resource 之前必须需要先加载别的 extension 的 resource。若是这些被依赖的 extension 无法被加载，在会在 `_check_faulty_extensions` 进行错误处理。

* `get_optional_extensions` 意味着加载 这个 extension 的 resource 之前可选的先加载别的 extension 的 resource。若是这些可选的 extension 无法被加载，则会对其进行忽略。

* `get_extended_resources` 是每个 extension 向外抛出 resource 的实现，这个方法是每个 extension 都会提供的，不然的话这个 extension 也就没意义了。

* `update_attributes_map` 则是对 extension 抛出的 resource 进行进一步的更新。 

### 构造 `/v2.0/` 的 Response

```
mapper.connect('index', '/', controller=Index(RESOURCES))
```

**作用：** 构造 `/v2.0/` 的 Response

```
RESOURCES = {'network': 'networks',
             'subnet': 'subnets',
             'subnetpool': 'subnetpools',
             'port': 'ports'}

class Index(wsgi.Application):
    def __init__(self, resources):
        self.resources = resources

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        metadata = {}

        layout = []
        for name, collection in six.iteritems(self.resources):
            href = urlparse.urljoin(req.path_url, collection)
            resource = {'name': name,
                        'collection': collection,
                        'links': [{'rel': 'self',
                                   'href': href}]}
            layout.append(resource)
        response = dict(resources=layout)
        content_type = req.best_match_content_type()
        body = wsgi.Serializer(metadata=metadata).serialize(response,
                                                            content_type)
        return webob.Response(body=body, content_type=content_type)
```

* `Index` 实例被声明为访问 `/` 时的 `controller`。

* `Index` 实现了用 `webob.dec.wsgify` 修饰的 `__call__`，当 `Index` 被实例化时，它就变成了一个可被调用的 wsgi app。

* 若想测试访问结果可用如下命令测试（请用自己的 token）：

```
curl -s -X GET http://172.16.100.106:9696/v2.0/ \
            -H "Content-Type: application/json" \
            -H "X-Auth-Token: 7eb90d76addc4a5bafeb380bf47f37fd"
```

* `Request` 和 `Serializer` 的实现我们以后再做探讨。