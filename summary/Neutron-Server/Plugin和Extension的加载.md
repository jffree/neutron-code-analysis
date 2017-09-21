# core plugin、service plugin 和 extension 的加载

## wsgi filter 和 app 的加载

在加载 `neutronapiapp_v2_0` 这个 Wsgi APP 的同时会做 core plugin、service plugin 和 extension 的加载。

`neutronapiapp_v2_0` 是通过 `neutronapi_v2_0` 来加载的：

在 *neutron/auth.py* 中的 `pipeline_factory` 方法完成的所有 wsgi app 和 wsgi filter 的加载：

```
def pipeline_factory(loader, global_conf, **local_conf):
    """Create a paste pipeline based on the 'auth_strategy' config option."""
    pipeline = local_conf[cfg.CONF.auth_strategy]
    pipeline = pipeline.split()
    filters = [loader.get_filter(n) for n in pipeline[:-1]] #加载 wsgi filter
    app = loader.get_app(pipeline[-1])  # 加载 wsgi app
    filters.reverse()
    for filter in filters:
        app = filter(app)
    return app
```

## plugin 和 extension 加载概述

Wsgi filter 中有一个名为 `extensions` 的 filter，其在 *neutron/api/extensions.py* 中实现：

```
def plugin_aware_extension_middleware_factory(global_config, **local_config):
    """Paste factory."""
    def _factory(app):
        ext_mgr = PluginAwareExtensionManager.get_instance()
        return ExtensionMiddleware(app, ext_mgr=ext_mgr)
    return _factory
```

* 可以看到，这个 filter 的主要作用就是完成的 `PluginAwareExtensionManager` 和 `ExtensionMiddleware` 的实例化，其中：
 1. `PluginAwareExtensionManager` 的实例化是调用 `PluginAwareExtensionManager.get_instance` 方法完成的，在这个方法中同时也完成了对 `NeutronManager` 的实例化
 2. `PluginAwareExtensionManager` 实例化的过程中（调用 `PluginAwareExtensionManager.__init__` 方法）完成了 extension 的加载
 3. `ExtensionMiddleware` 这个类完成了核心资源（`network、subnet、port、subnetpool`）之外的由 extension 实现的资源的路由映射。

*关于路由映射，在后面将会专门的文章进行讲解。*

### plugin 的加载过程

* 从概述中，我们知道了 plugin 的加载是由 `NeutronManager` 的初始化方法 `__init__` 完成的，具体分为两步：
 1. 从配置文件中找到 `core_plugin` 的定义，然后调用 `NeutronManager._get_plugin_instance` 来加载实现 core plugin 的类
 2. 调用 `NeutronManager._load_service_plugins` 加载所有的 service plugin
  * service plugin 有两部分，一部分是系统启动默认加载的 service plugin（通过 `NeutronManager._get_default_service_plugins` 方法获得），另一部分是在配置文件中通过 `service_plugins` 来指定的 

*最终 neutron-server 是将 core plugin 与 service plugin 放在了一起进行统一管理。*

### extension 的加载过程

* extension 的加载是在 `PluginAwareExtensionManager` 的初始化方法 `__init__` 中完成的，主要分为两部分
 1. 判断加载 extensions 的路径，也就是 `PluginAwareExtensionManager.__init__` 方法中的 `path` 变量。`get_extensions_path` 方法完成了 extensions 路径的确定，其判断方式有三点：
  1. neutron 的自带路径 `neutron.extensions`
  2. 所有 plugin （core and service）下的 `extension` 路径
  3. 在配置文件中通过 `api_extensions_path` 指定的路径
 2. 通过 `ExtensionManager._load_all_extensions` 从上一步获取的 path 中完成 extension 的加载：
  1. extension 的类名称是与其所在的模块的名称一致的，但是第一个字母大写（例如：`Address_scope` extension 就是在 *address_scope.py* 中实现的）。
  2. 加载 path 下所有的不以 `_` 开头的 `.py` 模块，并找到对应的 extension 类进行加载