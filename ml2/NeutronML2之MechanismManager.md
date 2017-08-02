# Neutron ML2 之 MechanismManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的网络实现机制实现插件式管理。

* 模块

*neutron/plugins/ml2/managers.py*

* 配置文件：

*/etc/neutron/neutron.conf*
*/etc/neutron/plugins/ml2/ml2_conf.ini*



## `__init__`

1. 调用 `super(MechanismManager, self)` 加载 neutron 网络实现驱动
2. 调用 `_register_mechanisms` 构造一个驱动名称与驱动实例映射的字典（`self.mech_drivers`），构造一个有序列表 `ordered_mech_drivers` 保存驱动实例
3. 调用 `is_host_filtering_supported` 判断是否所有的驱动都支持 **host filtering**

在 *setup.cfg* 文件中可以看到：

```
neutron.ml2.mechanism_drivers =
    logger = neutron.tests.unit.plugins.ml2.drivers.mechanism_logger:LoggerMechanismDriver
    test = neutron.tests.unit.plugins.ml2.drivers.mechanism_test:TestMechanismDriver
    linuxbridge = neutron.plugins.ml2.drivers.linuxbridge.mech_driver.mech_linuxbridge:LinuxbridgeMechanismDriver
    macvtap = neutron.plugins.ml2.drivers.macvtap.mech_driver.mech_macvtap:MacvtapMechanismDriver
    openvswitch = neutron.plugins.ml2.drivers.openvswitch.mech_driver.mech_openvswitch:OpenvswitchMechanismDriver
    l2population = neutron.plugins.ml2.drivers.l2pop.mech_driver:L2populationMechanismDriver
    sriovnicswitch = neutron.plugins.ml2.drivers.mech_sriov.mech_driver.mech_driver:SriovNicSwitchMechanismDriver
    fake_agent = neutron.tests.unit.plugins.ml2.drivers.mech_fake_agent:FakeAgentMechanismDriver
```

我们以 linuxbridge、openvswitch 以及 l2population 来进行分析。

## `def _register_mechanisms(self)`

## `def is_host_filtering_supported(self)`

循环调用驱动的 `is_host_filtering_supported` 方法，判断该驱动是否重写了 `filter_hosts_with_segment_access` 方法，若是驱动重写了该方法，则表示该驱动支持 **host filtering**，否则则是不支持。

## `def initialize(self)`

调用所有的 mechanism driver 的 `initialize` 方法

## `def supported_qos_rule_types(self)`

属性方法。查找所有加载的 mechanism driver 共同支持的 qos rule。

openvswitch 支持 `bandwidth_limit` 和 `dscp_marking`
linuxbridge 支持 `bandwidth_limit`
l2population 不支持任何 qos rule

所以，`supported_qos_rule_types` 得到的是个空列表

## `def create_network_precommit(self, context)`

1. 调用 `_check_vlan_transparency` 检查 mechanism driver 中是否支持 vlan 透传功能
2. 调用 `_call_on_drivers` 调用各个 mechanism driver 的 `create_network_precommit`

openvswitch 未实现 `create_network_precommit`
linuxbridge 未实现 `create_network_precommit`
l2population 未实现 `create_network_precommit`


## `def _check_vlan_transparency(self, context)`

调用所有加载的 mechanism driver 的 `check_vlan_transparency` 方法，来检查是否支持 vlan 透传功能。

若有一个 driver 不支持，则会引发异常

## `def _call_on_drivers(self, method_name, context, continue_on_failure=False, raise_db_retriable=False)`

调用各个 mechanism driver 的 method_name 方法

## `def create_network_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `create_network_postcommit`

openvswitch 未实现 `create_network_postcommit`
linuxbridge 未实现 `create_network_postcommit`
l2population 未实现 `create_network_postcommit`

## `def update_network_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `update_network_precommit`

openvswitch 未实现 `update_network_precommit`
linuxbridge 未实现 `update_network_precommit`
l2population 未实现 `update_network_precommit`

## `def update_network_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `update_network_postcommit`

openvswitch 未实现 `update_network_postcommit`
linuxbridge 未实现 `update_network_postcommit`
l2population 未实现 `update_network_postcommit`

## `def delete_network_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `delete_network_precommit`

openvswitch 未实现 `delete_network_precommit`
linuxbridge 未实现 `delete_network_precommit`
l2population 未实现 `delete_network_precommit`

## `def delete_network_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `delete_network_postcommit`

openvswitch 未实现 `delete_network_postcommit`
linuxbridge 未实现 `delete_network_postcommit`
l2population 未实现 `delete_network_postcommit`

## `def create_subnet_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `create_subnet_precommit`

openvswitch 未实现 `create_subnet_precommit`
linuxbridge 未实现 `create_subnet_precommit`
l2population 未实现 `create_subnet_precommit`

## `def create_subnet_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `create_subnet_postcommit`

openvswitch 未实现 `create_subnet_postcommit`
linuxbridge 未实现 `create_subnet_postcommit`
l2population 未实现 `create_subnet_postcommit`

## `def update_subnet_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `update_subnet_precommit`

openvswitch 未实现 `update_subnet_precommit`
linuxbridge 未实现 `update_subnet_precommit`
l2population 未实现 `update_subnet_precommit`

## `def update_subnet_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `update_subnet_postcommit`

openvswitch 未实现 `update_subnet_postcommit`
linuxbridge 未实现 `update_subnet_postcommit`
l2population 未实现 `update_subnet_postcommit`

## `def delete_subnet_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `delete_subnet_precommit`

openvswitch 未实现 `delete_subnet_precommit`
linuxbridge 未实现 `delete_subnet_precommit`
l2population 未实现 `delete_subnet_precommit`

## `def delete_subnet_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `delete_subnet_postcommit`

openvswitch 未实现 `delete_subnet_postcommit`
linuxbridge 未实现 `delete_subnet_postcommit`
l2population 未实现 `delete_subnet_postcommit`

## `def create_port_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `create_port_precommit`

openvswitch 和 linuxbridge 实现了 `create_port_precommit`（`AgentMechanismDriverBase`），用来创建该 port 的 `ProvisioningBlock` 记录
l2population 未实现 `create_port_precommit`

## `def create_port_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `create_port_postcommit`

openvswitch 未实现 `create_port_postcommit`
linuxbridge 未实现 `create_port_postcommit`
l2population 未实现 `create_port_postcommit`

## `def update_port_precommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `update_port_precommit`

openvswitch 和 linuxbridge 实现了 `update_port_precommit`（`AgentMechanismDriverBase`），用来创建该 port 的 `ProvisioningBlock` 记录
l2population 实现了 `update_port_precommit` 检查更新参数是否正确

## `def update_port_postcommit(self, context)`

通过调用 `_call_on_drivers` 调用各个 mechanism driver 的 `update_port_postcommit`

openvswitch 未实现 `update_port_postcommit`
linuxbridge 未实现 `update_port_postcommit`
l2population 实现了 `update_port_postcommit`

















