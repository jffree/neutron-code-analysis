# Neutron ML2 之 ExtensionManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的2层网络资源与其他资源的交互实现插件式管理。

* 模块

_neutron/plugins/ml2/managers.py_

* 配置文件：

_/etc/neutron/neutron.conf_  
_/etc/neutron/plugins/ml2/ml2\_conf.ini_

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













## `class ExtensionDriver(object)`

extension driver 实现的抽象基类

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






