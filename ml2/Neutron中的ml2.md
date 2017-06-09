# Neutron 中的 ml2

* ml2 的框架图：

![](https://www.ibm.com/developerworks/cn/cloud/library/cl-cn-openstackneutronml2/img002.png)

* ml2 的配置文件：*/etc/neutron/plugins/ml2/ml2_conf.ini*

## `__init__` 方法

```
    @resource_registry.tracked_resources(
        network=models_v2.Network,
        port=models_v2.Port,
        subnet=models_v2.Subnet,
        subnetpool=models_v2.SubnetPool,
        security_group=sg_models.SecurityGroup,
        security_group_rule=sg_models.SecurityGroupRule)
    def __init__(self):
        # First load drivers, then initialize DB, then initialize drivers
        self.type_manager = managers.TypeManager()
        self.extension_manager = managers.ExtensionManager()
        self.mechanism_manager = managers.MechanismManager()
        super(Ml2Plugin, self).__init__()
        self.type_manager.initialize()
        self.extension_manager.initialize()
        self.mechanism_manager.initialize()
        registry.subscribe(self._port_provisioned, resources.PORT,
                           provisioning_blocks.PROVISIONING_COMPLETE)
        registry.subscribe(self._handle_segment_change, resources.SEGMENT,
                           events.PRECOMMIT_CREATE)
        registry.subscribe(self._handle_segment_change, resources.SEGMENT,
                           events.PRECOMMIT_DELETE)
        registry.subscribe(self._handle_segment_change, resources.SEGMENT,
                           events.AFTER_CREATE)
        registry.subscribe(self._handle_segment_change, resources.SEGMENT,
                           events.AFTER_DELETE)
        self._setup_dhcp()
        self._start_rpc_notifiers()
        self.add_agent_status_check_worker(self.agent_health_check)
        self.add_workers(self.mechanism_manager.get_workers())
        self._verify_service_plugins_requirements()
        LOG.info(_LI("Modular L2 Plugin initialization complete"))
```

* `tracked_resources` 装饰器用于注册在 quota 中需要跟踪的资源

* `TypeManager` 网络类型管理（local,flat,vlan,gre,vxlan,geneve）

* `ExtensionManager` 扩展管理（port_security），用于管理和其他资源的交互

* `MechanismManager` 实现机制管理（openvswitch,linuxbridge）

* 订阅 `port` 资源的 `provisioning_complete` 的回调事件 `_port_provisioned`

* 订阅 `segment` 资源的 `precommit_create`、 `precommit_delete`、`after_create`、 `after_delete` 的回调事件 `_handle_segment_change`

* `_setup_dhcp`：加载 将网络调度到 dhcp agent 的驱动；设定每个一段时间检查 dhcp agent 的状态

* `_start_rpc_notifiers` 创建 ml2 的 rpc 客户端（`AgentNotifierApi`、`DhcpAgentNotifyAPI`）

* `add_workers` 增加机制端的 worker

* `_verify_service_plugins_requirements` 检查扩展管理是否已经加载了所有被需要的驱动。

### `TypeManager` 

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的网络类型实现插件式管理。

#### `__init__` 方法

```
    def __init__(self):
        # Mapping from type name to DriverManager
        self.drivers = {}

        LOG.info(_LI("Configured type driver names: %s"),
                 cfg.CONF.ml2.type_drivers)
        super(TypeManager, self).__init__('neutron.ml2.type_drivers',
                                          cfg.CONF.ml2.type_drivers,
                                          invoke_on_load=True)
        LOG.info(_LI("Loaded type driver names: %s"), self.names())
        self._register_types()
        self._check_tenant_network_types(cfg.CONF.ml2.tenant_network_types)
        self._check_external_network_type(cfg.CONF.ml2.external_network_type)
```

* 根据配置信息（cfg.CONF.ml2.type_drivers）加载所有的插件类，并且实例化（invoke_on_load=True）；

至于具体的插件类，我们 stup.cfg 文件：

```
neutron.ml2.type_drivers =
    flat = neutron.plugins.ml2.drivers.type_flat:FlatTypeDriver
    local = neutron.plugins.ml2.drivers.type_local:LocalTypeDriver
    vlan = neutron.plugins.ml2.drivers.type_vlan:VlanTypeDriver
    geneve = neutron.plugins.ml2.drivers.type_geneve:GeneveTypeDriver
    gre = neutron.plugins.ml2.drivers.type_gre:GreTypeDriver
    vxlan = neutron.plugins.ml2.drivers.type_vxlan:VxlanTypeDriver
```


* `_register_types` 用于构造一个类型名称与其实例的映射字典（`self.drivers[network_type] = ext`）

* `_check_tenant_network_types` 检查是否支持租户的网络类型（vxlan）

* `_check_external_network_type` 检查是否支持外网的网络类型（None）

#### `initialize`

```
    def initialize(self):
        for network_type, driver in six.iteritems(self.drivers):
            LOG.info(_LI("Initializing driver for type '%s'"), network_type)
            driver.obj.initialize()
```

* 调用实际类型实例的 `initialize` 方法

### `MechanismManager`

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的机制管理实现插件式管理。 

#### `__init__`

```
    def __init__(self):
        # Registered mechanism drivers, keyed by name.
        self.mech_drivers = {}
        # Ordered list of mechanism drivers, defining
        # the order in which the drivers are called.
        self.ordered_mech_drivers = []

        LOG.info(_LI("Configured mechanism driver names: %s"),
                 cfg.CONF.ml2.mechanism_drivers)
        super(MechanismManager, self).__init__('neutron.ml2.mechanism_drivers',
                                               cfg.CONF.ml2.mechanism_drivers,
                                               invoke_on_load=True,
                                               name_order=True)
        LOG.info(_LI("Loaded mechanism driver names: %s"), self.names())
        self._register_mechanisms()
        self.host_filtering_supported = self.is_host_filtering_supported()
        if not self.host_filtering_supported:
            LOG.warning(_LW("Host filtering is disabled because at least one "
                            "mechanism doesn't support it."))
```

* 根据配置信息（cfg.CONF.ml2.mechanism_drivers）加载所有的插件类，并且实例化（invoke_on_load=True）；

至于具体的插件类，我们 stup.cfg 文件：

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

* `_register_mechanisms` 构造一个映射一个列表：`mech_drivers` 保存插件名称与插件实例封装的映射；`ordered_mech_drivers` 插件的顺序列表

* `host_filtering_supported` 是否支持过滤主机

#### `initialize`

```
    def initialize(self):
        for driver in self.ordered_mech_drivers:
            LOG.info(_LI("Initializing mechanism driver '%s'"), driver.name)
            driver.obj.initialize()
```

* 同样是调用机制实例的 `initialize` 方法

### `ExtensionManager`

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的扩展管理实现插件式管理。 

#### `__init__` 方法

```
    def __init__(self):
        # Ordered list of extension drivers, defining
        # the order in which the drivers are called.
        self.ordered_ext_drivers = []

        LOG.info(_LI("Configured extension driver names: %s"),
                 cfg.CONF.ml2.extension_drivers)
        super(ExtensionManager, self).__init__('neutron.ml2.extension_drivers',
                                               cfg.CONF.ml2.extension_drivers,
                                               invoke_on_load=True,
                                               name_order=True)
        LOG.info(_LI("Loaded extension driver names: %s"), self.names())
        self._register_drivers()
```

* 根据配置信息（cfg.CONF.ml2.extension_drivers）加载所有的插件类，并且实例化（invoke_on_load=True）；

至于具体的插件类，我们 stup.cfg 文件：

```
neutron.ml2.extension_drivers =
    test = neutron.tests.unit.plugins.ml2.drivers.ext_test:TestExtensionDriver
    testdb = neutron.tests.unit.plugins.ml2.drivers.ext_test:TestDBExtensionDriver
    port_security = neutron.plugins.ml2.extensions.port_security:PortSecurityExtensionDriver
    qos = neutron.plugins.ml2.extensions.qos:QosExtensionDriver
    dns = neutron.plugins.ml2.extensions.dns_integration:DNSExtensionDriverML2
```

* 构造一个按顺序加载的扩展管理实例的封装列表 `ordered_ext_drivers`

#### `initialize`

```
    def initialize(self):
        # Initialize each driver in the list.
        for driver in self.ordered_ext_drivers:
            LOG.info(_LI("Initializing extension driver '%s'"), driver.name)
            driver.obj.initialize()
```

* 调用扩展的 `initialize` 方法

## `Ml2Plugin.__mro__`

```
<class 'neutron.plugins.ml2.plugin.Ml2Plugin'>, <class 'neutron.db.db_base_plugin_v2.NeutronDbPluginV2'>, <class 'neutron.db.db_base_plugin_common.DbBasePluginCommon'>, <class 'neutron.neutron_plugin_base_v2.NeutronPluginBaseV2'>, <class 'neutron.worker.WorkerSupportServiceMixin'>, <class 'neutron.db.rbac_db_mixin.RbacPluginMixin'>, <class 'neutron.db.common_db_mixin.CommonDbMixin'>, <class 'neutron.db.standardattrdescription_db.StandardAttrDescriptionMixin'>, <class 'neutron.db.dvr_mac_db.DVRDbMixin'>, <class 'neutron.extensions.dvr.DVRMacAddressPluginBase'>, <class 'neutron.db.external_net_db.External_net_db_mixin'>, <class 'neutron.db.securitygroups_rpc_base.SecurityGroupServerRpcMixin'>, <class 'neutron.db.securitygroups_db.SecurityGroupDbMixin'>, <class 'neutron.extensions.securitygroup.SecurityGroupPluginBase'>, <class 'neutron.db.agentschedulers_db.AZDhcpAgentSchedulerDbMixin'>, <class 'neutron.db.agentschedulers_db.DhcpAgentSchedulerDbMixin'>, <class 'neutron.extensions.dhcpagentscheduler.DhcpAgentSchedulerPluginBase'>, <class 'neutron.db.agentschedulers_db.AgentSchedulerDbMixin'>, <class 'neutron.db.agents_db.AgentDbMixin'>, <class 'neutron.extensions.agent.AgentPluginBase'>, <class 'neutron.db.agents_db.AgentAvailabilityZoneMixin'>, <class 'neutron.extensions.availability_zone.AvailabilityZonePluginBase'>, <class 'neutron.db.availability_zone.network.NetworkAvailabilityZoneMixin'>, <class 'neutron.extensions.network_availability_zone.NetworkAvailabilityZonePluginBase'>, <class 'neutron.db.allowedaddresspairs_db.AllowedAddressPairsMixin'>, <class 'neutron.db.vlantransparent_db.Vlantransparent_db_mixin'>, <class 'neutron.db.extradhcpopt_db.ExtraDhcpOptMixin'>, <class 'neutron.db.address_scope_db.AddressScopeDbMixin'>, <class 'neutron.extensions.address_scope.AddressScopePluginBase'>, <class 'neutron.db.subnet_service_type_db_models.SubnetServiceTypeMixin'>, <type 'object'>
```