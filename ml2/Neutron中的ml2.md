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

* `_setup_dhcp`：加载网络调度驱动 `cfg.CONF.network_scheduler_driver` ；设定每个一段时间检查 dhcp agent 的状态

* `_start_rpc_notifiers` 创建 ml2 的 rpc 客户端（`AgentNotifierApi`、`DhcpAgentNotifyAPI`）

* `add_workers` 增加机制端的 worker

* `_verify_service_plugins_requirements` 检查扩展管理是否已经加载了所有被需要的驱动。

## `Ml2Plugin.__mro__`

```
<class 'neutron.plugins.ml2.plugin.Ml2Plugin'>, <class 'neutron.db.db_base_plugin_v2.NeutronDbPluginV2'>, <class 'neutron.db.db_base_plugin_common.DbBasePluginCommon'>, <class 'neutron.neutron_plugin_base_v2.NeutronPluginBaseV2'>, <class 'neutron.worker.WorkerSupportServiceMixin'>, <class 'neutron.db.rbac_db_mixin.RbacPluginMixin'>, <class 'neutron.db.common_db_mixin.CommonDbMixin'>, <class 'neutron.db.standardattrdescription_db.StandardAttrDescriptionMixin'>, <class 'neutron.db.dvr_mac_db.DVRDbMixin'>, <class 'neutron.extensions.dvr.DVRMacAddressPluginBase'>, <class 'neutron.db.external_net_db.External_net_db_mixin'>, <class 'neutron.db.securitygroups_rpc_base.SecurityGroupServerRpcMixin'>, <class 'neutron.db.securitygroups_db.SecurityGroupDbMixin'>, <class 'neutron.extensions.securitygroup.SecurityGroupPluginBase'>, <class 'neutron.db.agentschedulers_db.AZDhcpAgentSchedulerDbMixin'>, <class 'neutron.db.agentschedulers_db.DhcpAgentSchedulerDbMixin'>, <class 'neutron.extensions.dhcpagentscheduler.DhcpAgentSchedulerPluginBase'>, <class 'neutron.db.agentschedulers_db.AgentSchedulerDbMixin'>, <class 'neutron.db.agents_db.AgentDbMixin'>, <class 'neutron.extensions.agent.AgentPluginBase'>, <class 'neutron.db.agents_db.AgentAvailabilityZoneMixin'>, <class 'neutron.extensions.availability_zone.AvailabilityZonePluginBase'>, <class 'neutron.db.availability_zone.network.NetworkAvailabilityZoneMixin'>, <class 'neutron.extensions.network_availability_zone.NetworkAvailabilityZonePluginBase'>, <class 'neutron.db.allowedaddresspairs_db.AllowedAddressPairsMixin'>, <class 'neutron.db.vlantransparent_db.Vlantransparent_db_mixin'>, <class 'neutron.db.extradhcpopt_db.ExtraDhcpOptMixin'>, <class 'neutron.db.address_scope_db.AddressScopeDbMixin'>, <class 'neutron.extensions.address_scope.AddressScopePluginBase'>, <class 'neutron.db.subnet_service_type_db_models.SubnetServiceTypeMixin'>, <type 'object'>
```

## 注册模型查询的钩子方法

```
    db_base_plugin_v2.NeutronDbPluginV2.register_model_query_hook(
        models_v2.Port,
        "ml2_port_bindings",
        '_ml2_port_model_hook',
        None,
        '_ml2_port_result_filter_hook')
```

### `def _ml2_port_model_hook(self, context, original_model, query)`

增加与 `PortBinding` 的绑定查询

### `def _ml2_port_result_filter_hook(self, query, filters)`

若过滤数据 `filters` 中含有 `binding:host_id` 的数据，则增加对该数据的过滤（前面已经增加了对 `PortBinding` 数据库的绑定）
















