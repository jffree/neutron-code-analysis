# Neutron ML2 之 TypeManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的网络类型实现插件式管理。

* 模块

_neutron/plugins/ml2/managers.py_

* 配置文件：

_/etc/neutron/neutron.conf_  
_/etc/neutron/plugins/ml2/ml2\_conf.ini_

* neutron 包信息文件

_setup.cfg_

## `__init__` 方法

1. 调用 `super(TypeManager, self).__init__` 加载 neutron 的类型驱动（`cfg.CONF.ml2.type_drivers`）
2. 调用 `_register_types` 构造一个类型名称与类型实例映射的字典（`self.drivers`）
3. 调用 `_check_tenant_network_types` 检查当前加载的网络类型中是否支持租户的网络类型（`cfg.CONF.ml2.tenant_network_types`）
4. 调用 `_check_external_network_type` 检查是否支持外网默认的网络类型（`cfg.CONF.ml2.external_network_type`）

_关于具体的配置信息，请大家参考手册。_

在 setup.cfg 中可以看到所有的 type driver：

```
neutron.ml2.type_drivers =
    flat = neutron.plugins.ml2.drivers.type_flat:FlatTypeDriver
    local = neutron.plugins.ml2.drivers.type_local:LocalTypeDriver
    vlan = neutron.plugins.ml2.drivers.type_vlan:VlanTypeDriver
    geneve = neutron.plugins.ml2.drivers.type_geneve:GeneveTypeDriver
    gre = neutron.plugins.ml2.drivers.type_gre:GreTypeDriver
    vxlan = neutron.plugins.ml2.drivers.type_vxlan:VxlanTypeDriver
```

## `def _register_types(self)`

## `def _check_tenant_network_types(self, types)`

## `def _check_external_network_type(self, ext_network_type)`

## `def initialize(self)`

调用所有的驱动模块的 `initialize` 方法

