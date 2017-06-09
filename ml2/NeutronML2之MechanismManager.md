# Neutron ML2 之 MechanismManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的网络实现机制实现插件式管理。

* 模块

*neutron/plugins/ml2/managers.py*

* 配置文件：

*/etc/neutron/neutron.conf*
*/etc/neutron/plugins/ml2/ml2_conf.ini*

* neutron 包信息文件

*setup.cfg*

## `__init__`

1. 调用 `super(MechanismManager, self)` 加载 neutron 网络实现驱动
2. 调用 `_register_mechanisms` 构造一个驱动名称与驱动实例映射的字典（`self.mech_drivers`），构造一个有序列表 `ordered_mech_drivers` 保存驱动实例
3. 调用 `is_host_filtering_supported` 判断是否所有的驱动都支持 **host filtering**

## `def _register_mechanisms(self)`

## `def is_host_filtering_supported(self)`

循环调用驱动的 `is_host_filtering_supported` 方法，判断该驱动是否重写了 `filter_hosts_with_segment_access` 方法，若是驱动重写了该方法，则表示该驱动支持 **host filtering**，否则则是不支持。