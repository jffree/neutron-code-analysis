# Neutron ML2 之 ExtensionManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的2层网络资源与其他资源的交互实现插件式管理。

_neutron/plugins/ml2/managers.py_

* 配置文件：

_/etc/neutron/neutron.conf_  
_/etc/neutron/plugins/ml2/ml2\_conf.ini_

* 作用

用于统一管理所有的 extension driver。这里的 extension 并没有单独拿到 *neutron/extension* 下，而是在 *neutron/plugins/ml2/extensions* 中存在。

## `def __init__(self):`

1. 调用 `super(ExtensionManager, self).__init__` 加载扩展驱动 `cfg.CONF.ml2.extension_drivers`
2. 调用 `_register_drivers` 创建一个列表 `ordered_ext_drivers` 用来保存被加载的实例

* 在 */etc/neutron/plugins/ml2/ml2_conf.ini* 文件中，我们看到 `extension_drivers` 的配置选项为：

```
[ml2]
....
extension_drivers = port_security
```

* 在 *setup.cfg* 文件中，我们看到

```
neutron.ml2.extension_drivers =
...
    port_security = neutron.plugins.ml2.extensions.port_security:PortSecurityExtensionDriver
```

## `def initialize(self)`

调用所有的驱动模块的 `initialize` 方法

## `def extend_subnet_dict(self, session, base_model, result)`

```
    def extend_subnet_dict(self, session, base_model, result):                                                                                                     
        """Notify all extension drivers to extend subnet dictionary."""
        self._call_on_dict_driver("extend_subnet_dict", session, base_model,
                                  result)
```

## `def extend_port_dict(self, session, base_model, result)`

```
    def extend_port_dict(self, session, base_model, result):                                                                                                           
        """Notify all extension drivers to extend port dictionary."""
        self._call_on_dict_driver("extend_port_dict", session, base_model,
                                  result)
```

## `def extend_subnet_dict(self, session, base_model, result)`

```
    def extend_subnet_dict(self, session, base_model, result):
        """Notify all extension drivers to extend subnet dictionary."""
        self._call_on_dict_driver("extend_subnet_dict", session, base_model,
                                  result)
```

## `def _call_on_dict_driver(self, method_name, session, base_model, result)`

```
    def _call_on_dict_driver(self, method_name, session, base_model, result):                                                                                          
        for driver in self.ordered_ext_drivers:
            try:
                getattr(driver.obj, method_name)(session, base_model, result)
            except Exception:
                LOG.error(_LE("Extension driver '%(name)s' failed in "
                          "%(method)s"),
                          {'name': driver.name, 'method': method_name})
                raise ml2_exc.ExtensionDriverError(driver=driver.name)
```

* 逻辑比较清楚，就是从驱动实例中获取相应的方法（主要是：`extend_subnet_dict`、`extend_port_dict` 和 `extend_subnet_dict`），进而再去调用，具体可去各个 driver 中查看

## `def extension_aliases(self)`

```
    def extension_aliases(self):                                                                                                                                       
        exts = []
        for driver in self.ordered_ext_drivers:
            alias = driver.obj.extension_alias
            if alias:
                exts.append(alias)
                LOG.info(_LI("Got %(alias)s extension from driver '%(drv)s'"),
                         {'alias': alias, 'drv': driver.name})
        return exts
```

获取所有驱动实例的别名

### `def process_create_network(self, plugin_context, data, result)`

```
    def process_create_network(self, plugin_context, data, result):                                                                                                    
        """Notify all extension drivers during network creation."""
        self._call_on_ext_drivers("process_create_network", plugin_context, data, result)
```

### `def process_update_network(self, plugin_context, data, result)`

```
    def process_update_network(self, plugin_context, data, result):                                                                                                    
        """Notify all extension drivers during network update."""
        self._call_on_ext_drivers("process_update_network", plugin_context,
                                  data, result)
```

### `def process_create_subnet(self, plugin_context, data, result)`

```
    def process_create_subnet(self, plugin_context, data, result):                                                                                                     
        """Notify all extension drivers during subnet creation."""
        self._call_on_ext_drivers("process_create_subnet", plugin_context,
                                  data, result)
```

### `def process_update_subnet(self, plugin_context, data, result)`

```
    def process_update_subnet(self, plugin_context, data, result):                                                                                                     
        """Notify all extension drivers during subnet update."""
        self._call_on_ext_drivers("process_update_subnet", plugin_context,
                                  data, result)
```

### `def process_create_port(self, plugin_context, data, result)`

```
    def process_create_port(self, plugin_context, data, result):                                                                                                       
        """Notify all extension drivers during port creation."""
        self._call_on_ext_drivers("process_create_port", plugin_context,
                                  data, result)
```

### `def process_update_port(self, plugin_context, data, result)`

```
    def process_update_port(self, plugin_context, data, result):                                                                                                       
        """Notify all extension drivers during port update."""
        self._call_on_ext_drivers("process_update_port", plugin_context,
                                  data, result)
```

### `def _call_on_ext_drivers(self, method_name, plugin_context, data, result)`

* `method_name`：需要在扩展驱动中调用的方法
* `plugin_context`：context
* `data`：租户准备创建的资源的请求数据
* `result`：之前创建步骤的执行结果（资源的创建时分步执行的，同样资源创建结果的数据也是累加的，最后呈现给用户的才是完整的）

```
    def _call_on_ext_drivers(self, method_name, plugin_context, data, result):                                                                                         
        """Helper method for calling a method across all extension drivers."""
        for driver in self.ordered_ext_drivers:
            try:
                getattr(driver.obj, method_name)(plugin_context, data, result)
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.info(_LI("Extension driver '%(name)s' failed in "
                             "%(method)s"),
                             {'name': driver.name, 'method': method_name})
```

## `class ExtensionDriver(object)`

extension driver 实现的抽象基类，除了 `initialize` 方法必须实现外，其余的方法都是可选的（因为有些 extension 可能支持 network 和 port，而不支持 subnet，所以有一部分的功能是没必要实现的，保持为空）。

从这个抽象基类就可以看出，这里的 extension 和 *neutron/extensions* 下模块的作用是一致的，是对 `network`、`subnet` 和 `port` 做了功能的扩展。

*neutron/plugins/ml2/driver_api.py*

```
@six.add_metaclass(abc.ABCMeta)
class ExtensionDriver(object):
```

### `def initialize(self)`

```
    @abc.abstractmethod
    def initialize(self):
```

抽象方法，子类中必须实现

### `def extension_alias(self)`

```
    @property
    def extension_alias(self):
        pass
```

### `def process_create_network(self, plugin_context, data, result)`

```
    def process_create_network(self, plugin_context, data, result)
        pass
```

### `def process_create_subnet(self, plugin_context, data, result)`

```
    def process_create_subnet(self, plugin_context, data, result)
        pass
```

### `def process_create_port(self, plugin_context, data, result)`

```
    def process_create_port(self, plugin_context, data, result)
        pass
```

### `def process_update_network(self, plugin_context, data, result)`

```
    def process_update_network(self, plugin_context, data, result)
        pass
```

### `def process_update_subnet(self, plugin_context, data, result)`

```
    def process_update_subnet(self, plugin_context, data, result)
        pass
```

### `def process_update_port(self, plugin_context, data, result)`

```
    def process_update_port(self, plugin_context, data, result)
        pass
```

### `def extend_network_dict(self, session, base_model, result)`

```
    def extend_network_dict(self, session, base_model, result)
        pass
```

### `def extend_subnet_dict(self, session, base_model, result)`

```
    def extend_subnet_dict(self, session, base_model, result)
        pass
```

### `def extend_port_dict(self, session, base_model, result)`

```
    def extend_port_dict(self, session, base_model, result)
        pass
```






