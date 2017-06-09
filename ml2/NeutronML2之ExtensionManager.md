# Neutron ML2 之 ExtensionManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的2层网络资源与其他资源的交互实现插件式管理。

* 模块

_neutron/plugins/ml2/managers.py_

* 配置文件：

_/etc/neutron/neutron.conf_  
_/etc/neutron/plugins/ml2/ml2\_conf.ini_

* neutron 包信息文件

_setup.cfg_

## `__init__`

1. 调用 `super(ExtensionManager, self).__init__` 加载扩展驱动 `cfg.CONF.ml2.extension_drivers`
2. 调用 `_register_drivers` 创建一个列表 `ordered_ext_drivers` 用来保存被加载的实例

## `def initialize(self)`

调用所有的驱动模块的 `initialize` 方法







