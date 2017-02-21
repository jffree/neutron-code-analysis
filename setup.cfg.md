### setup.cfg 中定义了 newton 的执行脚本、配置文件、服务以及接口。

setup.cfg 包含了相当丰富的信息，不过这里我们只关注 \[files\] 和 \[entry\_points\] 部分。

关于 setuptools、pip、pbr 可以参考我写的另一本 book ：understand python

我在最后列出了从源码安装neutron 的 log，比较长，有环境的同学可以在自己的环境中跑命令看一遍。

* **\[files\]：定义了 neutron 最为最顶层的包，确定了打包和安装时需要包含的配置文件和脚本文件**

```
[files]
packages = 
    neutron
data_files = 
    etc/neutron =
    etc/api-paste.ini
    etc/dhcp_agent.ini
    etc/fwaas_driver.ini
    etc/l3_agent.ini
    etc/lbaas_agent.ini
    etc/metadata_agent.ini
    etc/metering_agent.ini
    etc/policy.json
    etc/neutron.conf
    etc/rootwrap.conf
    etc/vpn_agent.ini
    etc/neutron/rootwrap.d =
    etc/neutron/rootwrap.d/debug.filters
    etc/neutron/rootwrap.d/dhcp.filters
    etc/neutron/rootwrap.d/iptables-firewall.filters
    etc/neutron/rootwrap.d/ipset-firewall.filters
    etc/neutron/rootwrap.d/l3.filters
    etc/neutron/rootwrap.d/lbaas-haproxy.filters
    etc/neutron/rootwrap.d/linuxbridge-plugin.filters
    etc/neutron/rootwrap.d/nec-plugin.filters
    etc/neutron/rootwrap.d/openvswitch-plugin.filters
    etc/neutron/rootwrap.d/ryu-plugin.filters
    etc/neutron/rootwrap.d/vpnaas.filters
    etc/init.d = etc/init.d/neutron-server
    etc/neutron/plugins/bigswitch =
    etc/neutron/plugins/bigswitch/restproxy.ini
    etc/neutron/plugins/bigswitch/ssl/ca_certs =
    etc/neutron/plugins/bigswitch/ssl/ca_certs/README
    etc/neutron/plugins/bigswitch/ssl/host_certs =
    etc/neutron/plugins/bigswitch/ssl/host_certs/README
    etc/neutron/plugins/brocade = etc/neutron/plugins/brocade/brocade.ini
    etc/neutron/plugins/cisco =
    etc/neutron/plugins/cisco/cisco_cfg_agent.ini
    etc/neutron/plugins/cisco/cisco_plugins.ini
    etc/neutron/plugins/cisco/cisco_router_plugin.ini
    etc/neutron/plugins/cisco/cisco_vpn_agent.ini
    etc/neutron/plugins/embrane = etc/neutron/plugins/embrane/heleos_conf.ini
    etc/neutron/plugins/hyperv = etc/neutron/plugins/hyperv/hyperv_neutron_plugin.ini
    etc/neutron/plugins/ibm = etc/neutron/plugins/ibm/sdnve_neutron_plugin.ini
    etc/neutron/plugins/linuxbridge = etc/neutron/plugins/linuxbridge/linuxbridge_conf.ini
    etc/neutron/plugins/metaplugin = etc/neutron/plugins/metaplugin/metaplugin.ini
    etc/neutron/plugins/midonet = etc/neutron/plugins/midonet/midonet.ini
    etc/neutron/plugins/ml2 =
    etc/neutron/plugins/bigswitch/restproxy.ini
    etc/neutron/plugins/ml2/ml2_conf.ini
    etc/neutron/plugins/ml2/ml2_conf_arista.ini
    etc/neutron/plugins/ml2/ml2_conf_brocade.ini
    etc/neutron/plugins/ml2/ml2_conf_cisco.ini
    etc/neutron/plugins/ml2/ml2_conf_mlnx.ini
    etc/neutron/plugins/ml2/ml2_conf_ncs.ini
    etc/neutron/plugins/ml2/ml2_conf_odl.ini
    etc/neutron/plugins/ml2/ml2_conf_ofa.ini
    etc/neutron/plugins/ml2/ml2_conf_fslsdn.ini
    etc/neutron/plugins/ml2/ml2_conf_sriov.ini
    etc/neutron/plugins/nuage/nuage_plugin.ini
    etc/neutron/plugins/mlnx = etc/neutron/plugins/mlnx/mlnx_conf.ini
    etc/neutron/plugins/nec = etc/neutron/plugins/nec/nec.ini
    etc/neutron/plugins/nuage = etc/neutron/plugins/nuage/nuage_plugin.ini
    etc/neutron/plugins/oneconvergence = etc/neutron/plugins/oneconvergence/nvsdplugin.ini
    etc/neutron/plugins/openvswitch = etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini
    etc/neutron/plugins/plumgrid = etc/neutron/plugins/plumgrid/plumgrid.ini
    etc/neutron/plugins/ryu = etc/neutron/plugins/ryu/ryu.ini
    etc/neutron/plugins/vmware = etc/neutron/plugins/vmware/nsx.ini
    etc/neutron/plugins/opencontrail = etc/neutron/plugins/opencontrail/contrailplugin.ini
scripts = 
    bin/neutron-rootwrap
    bin/neutron-rootwrap-xen-dom0
```

* **\[entry\_points\] 定义了 neutron 实现的脚本文件，各种的插件和服务接口**

```
[entry_points]
console_scripts = 
    neutron-cisco-cfg-agent = neutron.plugins.cisco.cfg_agent.cfg_agent:main
    neutron-check-nsx-config = neutron.plugins.vmware.check_nsx_config:main
    neutron-db-manage = neutron.db.migration.cli:main
    neutron-debug = neutron.debug.shell:main
    neutron-dhcp-agent = neutron.agent.dhcp_agent:main
    neutron-hyperv-agent = neutron.plugins.hyperv.agent.hyperv_neutron_agent:main
    neutron-ibm-agent = neutron.plugins.ibm.agent.sdnve_neutron_agent:main
    neutron-l3-agent = neutron.agent.l3_agent:main
    neutron-lbaas-agent = neutron.services.loadbalancer.agent.agent:main
    neutron-linuxbridge-agent = neutron.plugins.linuxbridge.agent.linuxbridge_neutron_agent:main
    neutron-metadata-agent = neutron.agent.metadata.agent:main
    neutron-mlnx-agent = neutron.plugins.mlnx.agent.eswitch_neutron_agent:main
    neutron-nec-agent = neutron.plugins.nec.agent.nec_neutron_agent:main
    neutron-netns-cleanup = neutron.agent.netns_cleanup_util:main
    neutron-ns-metadata-proxy = neutron.agent.metadata.namespace_proxy:main
    neutron-nsx-manage = neutron.plugins.vmware.shell:main
    neutron-nvsd-agent = neutron.plugins.oneconvergence.agent.nvsd_neutron_agent:main
    neutron-openvswitch-agent = neutron.plugins.openvswitch.agent.ovs_neutron_agent:main
    neutron-ovs-cleanup = neutron.agent.ovs_cleanup_util:main
    neutron-restproxy-agent = neutron.plugins.bigswitch.agent.restproxy_agent:main
    neutron-ryu-agent = neutron.plugins.ryu.agent.ryu_neutron_agent:main
    neutron-server = neutron.server:main
    neutron-rootwrap = oslo.rootwrap.cmd:main
    neutron-usage-audit = neutron.cmd.usage_audit:main
    neutron-vpn-agent = neutron.services.vpn.agent:main
    neutron-metering-agent = neutron.services.metering.agents.metering_agent:main
    neutron-ofagent-agent = neutron.plugins.ofagent.agent.main:main
    neutron-sriov-nic-agent = neutron.plugins.sriovnicagent.sriov_nic_agent:main
    neutron-sanity-check = neutron.cmd.sanity_check:main
neutron.core_plugins = 
    bigswitch = neutron.plugins.bigswitch.plugin:NeutronRestProxyV2
    brocade = neutron.plugins.brocade.NeutronPlugin:BrocadePluginV2
    cisco = neutron.plugins.cisco.network_plugin:PluginV2
    embrane = neutron.plugins.embrane.plugins.embrane_ml2_plugin:EmbraneMl2Plugin
    hyperv = neutron.plugins.hyperv.hyperv_neutron_plugin:HyperVNeutronPlugin
    ibm = neutron.plugins.ibm.sdnve_neutron_plugin:SdnvePluginV2
    midonet = neutron.plugins.midonet.plugin:MidonetPluginV2
    ml2 = neutron.plugins.ml2.plugin:Ml2Plugin
    mlnx = neutron.plugins.mlnx.mlnx_plugin:MellanoxEswitchPlugin
    nec = neutron.plugins.nec.nec_plugin:NECPluginV2
    nuage = neutron.plugins.nuage.plugin:NuagePlugin
    metaplugin = neutron.plugins.metaplugin.meta_neutron_plugin:MetaPluginV2
    oneconvergence = neutron.plugins.oneconvergence.plugin:OneConvergencePluginV2
    openvswitch = neutron.plugins.openvswitch.ovs_neutron_plugin:OVSNeutronPluginV2
    plumgrid = neutron.plugins.plumgrid.plumgrid_plugin.plumgrid_plugin:NeutronPluginPLUMgridV2
    ryu = neutron.plugins.ryu.ryu_neutron_plugin:RyuNeutronPluginV2
    vmware = neutron.plugins.vmware.plugin:NsxPlugin
neutron.service_plugins = 
    dummy = neutron.tests.unit.dummy_plugin:DummyServicePlugin
    router = neutron.services.l3_router.l3_router_plugin:L3RouterPlugin
    bigswitch_l3 = neutron.plugins.bigswitch.l3_router_plugin:L3RestProxy
    firewall = neutron.services.firewall.fwaas_plugin:FirewallPlugin
    lbaas = neutron.services.loadbalancer.plugin:LoadBalancerPlugin
    vpnaas = neutron.services.vpn.plugin:VPNDriverPlugin
    metering = neutron.services.metering.metering_plugin:MeteringPlugin
neutron.ml2.type_drivers = 
    flat = neutron.plugins.ml2.drivers.type_flat:FlatTypeDriver
    local = neutron.plugins.ml2.drivers.type_local:LocalTypeDriver
    vlan = neutron.plugins.ml2.drivers.type_vlan:VlanTypeDriver
    gre = neutron.plugins.ml2.drivers.type_gre:GreTypeDriver
    vxlan = neutron.plugins.ml2.drivers.type_vxlan:VxlanTypeDriver
neutron.ml2.mechanism_drivers = 
    opendaylight = neutron.plugins.ml2.drivers.mechanism_odl:OpenDaylightMechanismDriver
    logger = neutron.tests.unit.ml2.drivers.mechanism_logger:LoggerMechanismDriver
    test = neutron.tests.unit.ml2.drivers.mechanism_test:TestMechanismDriver
    bulkless = neutron.tests.unit.ml2.drivers.mechanism_bulkless:BulklessMechanismDriver
    linuxbridge = neutron.plugins.ml2.drivers.mech_linuxbridge:LinuxbridgeMechanismDriver
    openvswitch = neutron.plugins.ml2.drivers.mech_openvswitch:OpenvswitchMechanismDriver
    hyperv = neutron.plugins.ml2.drivers.mech_hyperv:HypervMechanismDriver
    ncs = neutron.plugins.ml2.drivers.mechanism_ncs:NCSMechanismDriver
    arista = neutron.plugins.ml2.drivers.arista.mechanism_arista:AristaDriver
    cisco_nexus = neutron.plugins.ml2.drivers.cisco.nexus.mech_cisco_nexus:CiscoNexusMechanismDriver
    cisco_apic = neutron.plugins.ml2.drivers.cisco.apic.mechanism_apic:APICMechanismDriver
    l2population = neutron.plugins.ml2.drivers.l2pop.mech_driver:L2populationMechanismDriver
    bigswitch = neutron.plugins.ml2.drivers.mech_bigswitch.driver:BigSwitchMechanismDriver
    ofagent = neutron.plugins.ml2.drivers.mech_ofagent:OfagentMechanismDriver
    mlnx = neutron.plugins.ml2.drivers.mlnx.mech_mlnx:MlnxMechanismDriver
    brocade = neutron.plugins.ml2.drivers.brocade.mechanism_brocade:BrocadeMechanism
    fslsdn = neutron.plugins.ml2.drivers.freescale.mechanism_fslsdn:FslsdnMechanismDriver
    sriovnicswitch = neutron.plugins.ml2.drivers.mech_sriov.mech_driver:SriovNicSwitchMechanismDriver
    nuage = neutron.plugins.ml2.drivers.mech_nuage.driver:NuageMechanismDriver
neutron.ml2.extension_drivers = 
    test = neutron.tests.unit.ml2.test_extension_driver_api:TestExtensionDriver
neutron.openstack.common.cache.backends = 
    memory = neutron.openstack.common.cache._backends.memory:MemoryBackend
oslo.messaging.notify.drivers = 
    neutron.openstack.common.notifier.log_notifier = oslo.messaging.notify._impl_log:LogDriver
    neutron.openstack.common.notifier.no_op_notifier = oslo.messaging.notify._impl_noop:NoOpDriver
    neutron.openstack.common.notifier.rpc_notifier2 = oslo.messaging.notify._impl_messaging:MessagingV2Driver
    neutron.openstack.common.notifier.rpc_notifier = oslo.messaging.notify._impl_messaging:MessagingDriver
    neutron.openstack.common.notifier.test_notifier = oslo.messaging.notify._impl_test:TestDriver
```

* **我用 **`python setup.py install --dry-run 2>&1> install.log`** 命令打出了从源码安装neutron的log**

```
running install
[pbr] Writing ChangeLog
[pbr] Generating ChangeLog
[pbr] ChangeLog complete (0.0s)
[pbr] Generating AUTHORS
[pbr] AUTHORS complete (0.0s)
running build
running build_py
creating build
creating build/lib
creating build/lib/neutron
creating build/lib/neutron/plugins
creating build/lib/neutron/plugins/vmware
creating build/lib/neutron/plugins/vmware/vshield
creating build/lib/neutron/plugins/vmware/vshield/tasks
copying neutron/plugins/vmware/vshield/tasks/__init__.py -> build/lib/neutron/plugins/vmware/vshield/tasks
copying neutron/plugins/vmware/vshield/tasks/constants.py -> build/lib/neutron/plugins/vmware/vshield/tasks
copying neutron/plugins/vmware/vshield/tasks/tasks.py -> build/lib/neutron/plugins/vmware/vshield/tasks
creating build/lib/neutron/tests
creating build/lib/neutron/tests/unit
creating build/lib/neutron/tests/unit/db
creating build/lib/neutron/tests/unit/db/loadbalancer
copying neutron/tests/unit/db/loadbalancer/__init__.py -> build/lib/neutron/tests/unit/db/loadbalancer
copying neutron/tests/unit/db/loadbalancer/test_db_loadbalancer.py -> build/lib/neutron/tests/unit/db/loadbalancer
creating build/lib/neutron/plugins/ml2
creating build/lib/neutron/plugins/ml2/drivers
creating build/lib/neutron/plugins/ml2/drivers/brocade
copying neutron/plugins/ml2/drivers/brocade/__init__.py -> build/lib/neutron/plugins/ml2/drivers/brocade
copying neutron/plugins/ml2/drivers/brocade/mechanism_brocade.py -> build/lib/neutron/plugins/ml2/drivers/brocade
creating build/lib/neutron/plugins/ryu
copying neutron/plugins/ryu/__init__.py -> build/lib/neutron/plugins/ryu
copying neutron/plugins/ryu/ryu_neutron_plugin.py -> build/lib/neutron/plugins/ryu
creating build/lib/neutron/api
creating build/lib/neutron/api/rpc
copying neutron/api/rpc/__init__.py -> build/lib/neutron/api/rpc
creating build/lib/neutron/db
creating build/lib/neutron/db/migration
creating build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/vmware_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/ovs_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/__init__.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/other_extensions_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/core_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/metering_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/mlnx_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/cisco_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/ryu_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/l3_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/loadbalancer_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/env.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/portsec_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/firewall_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/other_plugins_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/heal_script.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/agent_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/lb_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/vpn_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/ml2_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/brocade_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/secgroup_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
copying neutron/db/migration/alembic_migrations/nec_init_ops.py -> build/lib/neutron/db/migration/alembic_migrations
creating build/lib/neutron/plugins/midonet
copying neutron/plugins/midonet/__init__.py -> build/lib/neutron/plugins/midonet
copying neutron/plugins/midonet/plugin.py -> build/lib/neutron/plugins/midonet
copying neutron/plugins/midonet/midonet_lib.py -> build/lib/neutron/plugins/midonet
creating build/lib/neutron/tests/functional
copying neutron/tests/functional/__init__.py -> build/lib/neutron/tests/functional
copying neutron/tests/functional/base.py -> build/lib/neutron/tests/functional
creating build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/combined.py -> build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/__init__.py -> build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/migration.py -> build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/constants.py -> build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/rpc.py -> build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/nsx.py -> build/lib/neutron/plugins/vmware/dhcp_meta
copying neutron/plugins/vmware/dhcp_meta/lsnmanager.py -> build/lib/neutron/plugins/vmware/dhcp_meta
creating build/lib/neutron/plugins/openvswitch
copying neutron/plugins/openvswitch/__init__.py -> build/lib/neutron/plugins/openvswitch
copying neutron/plugins/openvswitch/ovs_models_v2.py -> build/lib/neutron/plugins/openvswitch
copying neutron/plugins/vmware/vshield/__init__.py -> build/lib/neutron/plugins/vmware/vshield
copying neutron/plugins/vmware/vshield/vcns.py -> build/lib/neutron/plugins/vmware/vshield
copying neutron/plugins/vmware/vshield/edge_appliance_driver.py -> build/lib/neutron/plugins/vmware/vshield
copying neutron/plugins/vmware/vshield/vcns_driver.py -> build/lib/neutron/plugins/vmware/vshield
copying neutron/plugins/vmware/vshield/edge_firewall_driver.py -> build/lib/neutron/plugins/vmware/vshield
copying neutron/plugins/vmware/vshield/edge_loadbalancer_driver.py -> build/lib/neutron/plugins/vmware/vshield
copying neutron/plugins/vmware/vshield/edge_ipsecvpn_driver.py -> build/lib/neutron/plugins/vmware/vshield
creating build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/__init__.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/fake_oflib.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/test_arp_lib.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/test_ofa_flows.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/test_ofa_ports.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/test_ofswitch.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/ofa_test_base.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/test_ofa_neutron_agent.py -> build/lib/neutron/tests/unit/ofagent
copying neutron/tests/unit/ofagent/test_ofa_defaults.py -> build/lib/neutron/tests/unit/ofagent
creating build/lib/neutron/services
creating build/lib/neutron/services/firewall
creating build/lib/neutron/services/firewall/agents
creating build/lib/neutron/services/firewall/agents/varmour
copying neutron/services/firewall/agents/varmour/__init__.py -> build/lib/neutron/services/firewall/agents/varmour
copying neutron/services/firewall/agents/varmour/varmour_router.py -> build/lib/neutron/services/firewall/agents/varmour
copying neutron/services/firewall/agents/varmour/varmour_utils.py -> build/lib/neutron/services/firewall/agents/varmour
copying neutron/services/firewall/agents/varmour/varmour_api.py -> build/lib/neutron/services/firewall/agents/varmour
copying neutron/plugins/__init__.py -> build/lib/neutron/plugins
creating build/lib/neutron/plugins/mlnx
creating build/lib/neutron/plugins/mlnx/db
copying neutron/plugins/mlnx/db/__init__.py -> build/lib/neutron/plugins/mlnx/db
copying neutron/plugins/mlnx/db/mlnx_db_v2.py -> build/lib/neutron/plugins/mlnx/db
copying neutron/plugins/mlnx/db/mlnx_models_v2.py -> build/lib/neutron/plugins/mlnx/db
creating build/lib/neutron/services/metering
creating build/lib/neutron/services/metering/drivers
creating build/lib/neutron/services/metering/drivers/noop
copying neutron/services/metering/drivers/noop/__init__.py -> build/lib/neutron/services/metering/drivers/noop
copying neutron/services/metering/drivers/noop/noop_driver.py -> build/lib/neutron/services/metering/drivers/noop
creating build/lib/neutron/services/loadbalancer
creating build/lib/neutron/services/loadbalancer/drivers
creating build/lib/neutron/services/loadbalancer/drivers/haproxy
copying neutron/services/loadbalancer/drivers/haproxy/cfg.py -> build/lib/neutron/services/loadbalancer/drivers/haproxy
copying neutron/services/loadbalancer/drivers/haproxy/__init__.py -> build/lib/neutron/services/loadbalancer/drivers/haproxy
copying neutron/services/loadbalancer/drivers/haproxy/plugin_driver.py -> build/lib/neutron/services/loadbalancer/drivers/haproxy
copying neutron/services/loadbalancer/drivers/haproxy/namespace_driver.py -> build/lib/neutron/services/loadbalancer/drivers/haproxy
creating build/lib/neutron/tests/unit/ml2
creating build/lib/neutron/tests/unit/ml2/drivers
creating build/lib/neutron/tests/unit/ml2/drivers/cisco
copying neutron/tests/unit/ml2/drivers/cisco/__init__.py -> build/lib/neutron/tests/unit/ml2/drivers/cisco
creating build/lib/neutron/services/vpn
creating build/lib/neutron/services/vpn/service_drivers
copying neutron/services/vpn/service_drivers/cisco_csr_db.py -> build/lib/neutron/services/vpn/service_drivers
copying neutron/services/vpn/service_drivers/__init__.py -> build/lib/neutron/services/vpn/service_drivers
copying neutron/services/vpn/service_drivers/ipsec.py -> build/lib/neutron/services/vpn/service_drivers
copying neutron/services/vpn/service_drivers/cisco_validator.py -> build/lib/neutron/services/vpn/service_drivers
copying neutron/services/vpn/service_drivers/cisco_cfg_loader.py -> build/lib/neutron/services/vpn/service_drivers
copying neutron/services/vpn/service_drivers/cisco_ipsec.py -> build/lib/neutron/services/vpn/service_drivers
creating build/lib/neutron/services/vpn/common
copying neutron/services/vpn/common/__init__.py -> build/lib/neutron/services/vpn/common
copying neutron/services/vpn/common/topics.py -> build/lib/neutron/services/vpn/common
creating build/lib/neutron/plugins/vmware/vshield/common
copying neutron/plugins/vmware/vshield/common/__init__.py -> build/lib/neutron/plugins/vmware/vshield/common
copying neutron/plugins/vmware/vshield/common/constants.py -> build/lib/neutron/plugins/vmware/vshield/common
copying neutron/plugins/vmware/vshield/common/VcnsApiClient.py -> build/lib/neutron/plugins/vmware/vshield/common
copying neutron/plugins/vmware/vshield/common/exceptions.py -> build/lib/neutron/plugins/vmware/vshield/common
creating build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/__init__.py -> build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/securitygroups.py -> build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/config.py -> build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/exceptions.py -> build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/nsx_utils.py -> build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/sync.py -> build/lib/neutron/plugins/vmware/common
copying neutron/plugins/vmware/common/utils.py -> build/lib/neutron/plugins/vmware/common
creating build/lib/neutron/plugins/ml2/drivers/mech_sriov
copying neutron/plugins/ml2/drivers/mech_sriov/__init__.py -> build/lib/neutron/plugins/ml2/drivers/mech_sriov
copying neutron/plugins/ml2/drivers/mech_sriov/mech_driver.py -> build/lib/neutron/plugins/ml2/drivers/mech_sriov
creating build/lib/neutron/services/metering/agents
copying neutron/services/metering/agents/__init__.py -> build/lib/neutron/services/metering/agents
copying neutron/services/metering/agents/metering_agent.py -> build/lib/neutron/services/metering/agents
creating build/lib/neutron/db/loadbalancer
copying neutron/db/loadbalancer/__init__.py -> build/lib/neutron/db/loadbalancer
copying neutron/db/loadbalancer/loadbalancer_db.py -> build/lib/neutron/db/loadbalancer
creating build/lib/neutron/plugins/ofagent
creating build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/flows.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/__init__.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/main.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/ports.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/tables.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/constants.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/ofa_neutron_agent.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/arp_lib.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/metadata.py -> build/lib/neutron/plugins/ofagent/agent
copying neutron/plugins/ofagent/agent/ofswitch.py -> build/lib/neutron/plugins/ofagent/agent
creating build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/__init__.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_agent_scheduler.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_rpcapi.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_mlnx_comm_utils.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_mlnx_neutron_agent.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_mlnx_db.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_mlnx_security_group.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_mlnx_plugin.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_mlnx_plugin_config.py -> build/lib/neutron/tests/unit/mlnx
copying neutron/tests/unit/mlnx/test_defaults.py -> build/lib/neutron/tests/unit/mlnx
creating build/lib/neutron/agent
creating build/lib/neutron/agent/linux
copying neutron/agent/linux/async_process.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/__init__.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/external_process.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/dhcp.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/ip_lib.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/interface.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/ipset_manager.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/daemon.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/ovs_lib.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/polling.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/iptables_manager.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/iptables_firewall.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/ovsdb_monitor.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/ra.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/utils.py -> build/lib/neutron/agent/linux
copying neutron/agent/linux/keepalived.py -> build/lib/neutron/agent/linux
creating build/lib/neutron/plugins/nec
copying neutron/plugins/nec/nec_router.py -> build/lib/neutron/plugins/nec
copying neutron/plugins/nec/__init__.py -> build/lib/neutron/plugins/nec
copying neutron/plugins/nec/packet_filter.py -> build/lib/neutron/plugins/nec
copying neutron/plugins/nec/router_drivers.py -> build/lib/neutron/plugins/nec
copying neutron/plugins/nec/ofc_manager.py -> build/lib/neutron/plugins/nec
copying neutron/plugins/nec/nec_plugin.py -> build/lib/neutron/plugins/nec
copying neutron/plugins/nec/ofc_driver_base.py -> build/lib/neutron/plugins/nec
creating build/lib/neutron/tests/unit/services
creating build/lib/neutron/tests/unit/services/loadbalancer
creating build/lib/neutron/tests/unit/services/loadbalancer/drivers
creating build/lib/neutron/tests/unit/services/loadbalancer/drivers/logging_noop
copying neutron/tests/unit/services/loadbalancer/drivers/logging_noop/__init__.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/logging_noop
copying neutron/tests/unit/services/loadbalancer/drivers/logging_noop/test_logging_noop_driver.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/logging_noop
creating build/lib/neutron/plugins/cisco
creating build/lib/neutron/plugins/cisco/l3
copying neutron/plugins/cisco/l3/service_vm_lib.py -> build/lib/neutron/plugins/cisco/l3
copying neutron/plugins/cisco/l3/__init__.py -> build/lib/neutron/plugins/cisco/l3
creating build/lib/neutron/tests/unit/ml2/drivers/mech_sriov
copying neutron/tests/unit/ml2/drivers/mech_sriov/__init__.py -> build/lib/neutron/tests/unit/ml2/drivers/mech_sriov
copying neutron/tests/unit/ml2/drivers/mech_sriov/test_mech_sriov_nic_switch.py -> build/lib/neutron/tests/unit/ml2/drivers/mech_sriov
creating build/lib/neutron/tests/unit/services/firewall
creating build/lib/neutron/tests/unit/services/firewall/agents
copying neutron/tests/unit/services/firewall/agents/__init__.py -> build/lib/neutron/tests/unit/services/firewall/agents
copying neutron/tests/unit/services/firewall/agents/test_firewall_agent_api.py -> build/lib/neutron/tests/unit/services/firewall/agents
creating build/lib/neutron/plugins/ryu/common
copying neutron/plugins/ryu/common/__init__.py -> build/lib/neutron/plugins/ryu/common
copying neutron/plugins/ryu/common/config.py -> build/lib/neutron/plugins/ryu/common
creating build/lib/neutron/plugins/common
copying neutron/plugins/common/__init__.py -> build/lib/neutron/plugins/common
copying neutron/plugins/common/constants.py -> build/lib/neutron/plugins/common
copying neutron/plugins/common/utils.py -> build/lib/neutron/plugins/common
creating build/lib/neutron/api/rpc/handlers
copying neutron/api/rpc/handlers/__init__.py -> build/lib/neutron/api/rpc/handlers
copying neutron/api/rpc/handlers/l3_rpc.py -> build/lib/neutron/api/rpc/handlers
copying neutron/api/rpc/handlers/dvr_rpc.py -> build/lib/neutron/api/rpc/handlers
copying neutron/api/rpc/handlers/dhcp_rpc.py -> build/lib/neutron/api/rpc/handlers
copying neutron/api/rpc/handlers/securitygroups_rpc.py -> build/lib/neutron/api/rpc/handlers
creating build/lib/neutron/tests/unit/services/loadbalancer/drivers/a10networks
copying neutron/tests/unit/services/loadbalancer/drivers/a10networks/__init__.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/a10networks
copying neutron/tests/unit/services/loadbalancer/drivers/a10networks/test_driver_v1.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/a10networks
creating build/lib/neutron/hacking
copying neutron/hacking/__init__.py -> build/lib/neutron/hacking
copying neutron/hacking/checks.py -> build/lib/neutron/hacking
creating build/lib/neutron/plugins/nuage
creating build/lib/neutron/plugins/nuage/common
copying neutron/plugins/nuage/common/__init__.py -> build/lib/neutron/plugins/nuage/common
copying neutron/plugins/nuage/common/constants.py -> build/lib/neutron/plugins/nuage/common
copying neutron/plugins/nuage/common/config.py -> build/lib/neutron/plugins/nuage/common
copying neutron/plugins/nuage/common/exceptions.py -> build/lib/neutron/plugins/nuage/common
creating build/lib/neutron/tests/unit/services/loadbalancer/agent
copying neutron/tests/unit/services/loadbalancer/agent/__init__.py -> build/lib/neutron/tests/unit/services/loadbalancer/agent
copying neutron/tests/unit/services/loadbalancer/agent/test_agent_manager.py -> build/lib/neutron/tests/unit/services/loadbalancer/agent
copying neutron/tests/unit/services/loadbalancer/agent/test_agent.py -> build/lib/neutron/tests/unit/services/loadbalancer/agent
copying neutron/tests/unit/services/loadbalancer/agent/test_api.py -> build/lib/neutron/tests/unit/services/loadbalancer/agent
copying neutron/tests/unit/ml2/test_mech_openvswitch.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_type_vxlan.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/__init__.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_security_group.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_type_vlan.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_extension_driver_api.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_type_gre.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_agent_scheduler.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_mech_hyperv.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_rpcapi.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_port_binding.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_driver_context.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_mechanism_odl.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_mech_linuxbridge.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_helpers.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/_test_mech_agent.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_mechanism_ncs.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_type_flat.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_type_local.py -> build/lib/neutron/tests/unit/ml2
copying neutron/tests/unit/ml2/test_ml2_plugin.py -> build/lib/neutron/tests/unit/ml2
creating build/lib/neutron/services/loadbalancer/drivers/embrane
creating build/lib/neutron/services/loadbalancer/drivers/embrane/agent
copying neutron/services/loadbalancer/drivers/embrane/agent/dispatcher.py -> build/lib/neutron/services/loadbalancer/drivers/embrane/agent
copying neutron/services/loadbalancer/drivers/embrane/agent/__init__.py -> build/lib/neutron/services/loadbalancer/drivers/embrane/agent
copying neutron/services/loadbalancer/drivers/embrane/agent/lb_operations.py -> build/lib/neutron/services/loadbalancer/drivers/embrane/agent
creating build/lib/neutron/plugins/opencontrail
creating build/lib/neutron/plugins/opencontrail/common
copying neutron/plugins/opencontrail/common/__init__.py -> build/lib/neutron/plugins/opencontrail/common
copying neutron/plugins/opencontrail/common/exceptions.py -> build/lib/neutron/plugins/opencontrail/common
copying neutron/plugins/vmware/__init__.py -> build/lib/neutron/plugins/vmware
copying neutron/plugins/vmware/plugin.py -> build/lib/neutron/plugins/vmware
copying neutron/plugins/vmware/check_nsx_config.py -> build/lib/neutron/plugins/vmware
copying neutron/plugins/vmware/dhcpmeta_modes.py -> build/lib/neutron/plugins/vmware
copying neutron/plugins/vmware/nsx_cluster.py -> build/lib/neutron/plugins/vmware
copying neutron/services/loadbalancer/__init__.py -> build/lib/neutron/services/loadbalancer
copying neutron/services/loadbalancer/plugin.py -> build/lib/neutron/services/loadbalancer
copying neutron/services/loadbalancer/constants.py -> build/lib/neutron/services/loadbalancer
copying neutron/services/loadbalancer/agent_scheduler.py -> build/lib/neutron/services/loadbalancer
copying neutron/services/vpn/__init__.py -> build/lib/neutron/services/vpn
copying neutron/services/vpn/plugin.py -> build/lib/neutron/services/vpn
copying neutron/services/vpn/agent.py -> build/lib/neutron/services/vpn
creating build/lib/neutron/plugins/ibm
creating build/lib/neutron/plugins/ibm/common
copying neutron/plugins/ibm/common/__init__.py -> build/lib/neutron/plugins/ibm/common
copying neutron/plugins/ibm/common/constants.py -> build/lib/neutron/plugins/ibm/common
copying neutron/plugins/ibm/common/config.py -> build/lib/neutron/plugins/ibm/common
copying neutron/plugins/ibm/common/exceptions.py -> build/lib/neutron/plugins/ibm/common
creating build/lib/neutron/tests/unit/services/firewall/drivers
copying neutron/tests/unit/services/firewall/drivers/__init__.py -> build/lib/neutron/tests/unit/services/firewall/drivers
creating build/lib/neutron/plugins/linuxbridge
creating build/lib/neutron/plugins/linuxbridge/db
copying neutron/plugins/linuxbridge/db/__init__.py -> build/lib/neutron/plugins/linuxbridge/db
copying neutron/plugins/linuxbridge/db/l2network_models_v2.py -> build/lib/neutron/plugins/linuxbridge/db
creating build/lib/neutron/plugins/ml2/drivers/arista
copying neutron/plugins/ml2/drivers/arista/__init__.py -> build/lib/neutron/plugins/ml2/drivers/arista
copying neutron/plugins/ml2/drivers/arista/config.py -> build/lib/neutron/plugins/ml2/drivers/arista
copying neutron/plugins/ml2/drivers/arista/arista_l3_driver.py -> build/lib/neutron/plugins/ml2/drivers/arista
copying neutron/plugins/ml2/drivers/arista/exceptions.py -> build/lib/neutron/plugins/ml2/drivers/arista
copying neutron/plugins/ml2/drivers/arista/db.py -> build/lib/neutron/plugins/ml2/drivers/arista
copying neutron/plugins/ml2/drivers/arista/mechanism_arista.py -> build/lib/neutron/plugins/ml2/drivers/arista
creating build/lib/neutron/plugins/oneconvergence
creating build/lib/neutron/plugins/oneconvergence/agent
copying neutron/plugins/oneconvergence/agent/__init__.py -> build/lib/neutron/plugins/oneconvergence/agent
copying neutron/plugins/oneconvergence/agent/nvsd_neutron_agent.py -> build/lib/neutron/plugins/oneconvergence/agent
copying neutron/plugins/opencontrail/__init__.py -> build/lib/neutron/plugins/opencontrail
copying neutron/plugins/opencontrail/contrail_plugin.py -> build/lib/neutron/plugins/opencontrail
creating build/lib/neutron/tests/unit/vmware
creating build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/__init__.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_vcns_driver.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_lbaas_plugin.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_fwaas_plugin.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_edge_router.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_vpnaas_plugin.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_loadbalancer_driver.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/test_firewall_driver.py -> build/lib/neutron/tests/unit/vmware/vshield
copying neutron/tests/unit/vmware/vshield/fake_vcns.py -> build/lib/neutron/tests/unit/vmware/vshield
creating build/lib/neutron/agent/common
copying neutron/agent/common/__init__.py -> build/lib/neutron/agent/common
copying neutron/agent/common/config.py -> build/lib/neutron/agent/common
creating build/lib/neutron/plugins/nec/agent
copying neutron/plugins/nec/agent/__init__.py -> build/lib/neutron/plugins/nec/agent
copying neutron/plugins/nec/agent/nec_neutron_agent.py -> build/lib/neutron/plugins/nec/agent
creating build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/test_ryu_security_group.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/__init__.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/test_ryu_agent.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/test_ryu_db.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/test_ryu_plugin.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/fake_ryu.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/ryu/test_defaults.py -> build/lib/neutron/tests/unit/ryu
copying neutron/tests/unit/vmware/test_nsx_utils.py -> build/lib/neutron/tests/unit/vmware
copying neutron/tests/unit/vmware/test_nsx_plugin.py -> build/lib/neutron/tests/unit/vmware
copying neutron/tests/unit/vmware/__init__.py -> build/lib/neutron/tests/unit/vmware
copying neutron/tests/unit/vmware/test_agent_scheduler.py -> build/lib/neutron/tests/unit/vmware
copying neutron/tests/unit/vmware/test_nsx_sync.py -> build/lib/neutron/tests/unit/vmware
copying neutron/tests/unit/vmware/test_dhcpmeta.py -> build/lib/neutron/tests/unit/vmware
copying neutron/tests/unit/vmware/test_nsx_opts.py -> build/lib/neutron/tests/unit/vmware
creating build/lib/neutron/api/rpc/agentnotifiers
copying neutron/api/rpc/agentnotifiers/__init__.py -> build/lib/neutron/api/rpc/agentnotifiers
copying neutron/api/rpc/agentnotifiers/dhcp_rpc_agent_api.py -> build/lib/neutron/api/rpc/agentnotifiers
copying neutron/api/rpc/agentnotifiers/l3_rpc_agent_api.py -> build/lib/neutron/api/rpc/agentnotifiers
copying neutron/api/rpc/agentnotifiers/metering_rpc_agent_api.py -> build/lib/neutron/api/rpc/agentnotifiers
creating build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/policy_profile.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/__init__.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/_credential_view.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/qos.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/network_profile.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/credential.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/n1kv.py -> build/lib/neutron/plugins/cisco/extensions
copying neutron/plugins/cisco/extensions/_qos_view.py -> build/lib/neutron/plugins/cisco/extensions
creating build/lib/neutron/services/l3_router
creating build/lib/neutron/services/l3_router/brocade
copying neutron/services/l3_router/brocade/__init__.py -> build/lib/neutron/services/l3_router/brocade
copying neutron/services/l3_router/brocade/l3_router_plugin.py -> build/lib/neutron/services/l3_router/brocade
copying neutron/services/firewall/agents/__init__.py -> build/lib/neutron/services/firewall/agents
copying neutron/services/firewall/agents/firewall_agent_api.py -> build/lib/neutron/services/firewall/agents
copying neutron/plugins/mlnx/__init__.py -> build/lib/neutron/plugins/mlnx
copying neutron/plugins/mlnx/rpc_callbacks.py -> build/lib/neutron/plugins/mlnx
copying neutron/plugins/mlnx/mlnx_plugin.py -> build/lib/neutron/plugins/mlnx
copying neutron/plugins/mlnx/agent_notify_api.py -> build/lib/neutron/plugins/mlnx
creating build/lib/neutron/plugins/cisco/cfg_agent
creating build/lib/neutron/plugins/cisco/cfg_agent/device_drivers
creating build/lib/neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv
copying neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv/__init__.py -> build/lib/neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv
copying neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv/csr1kv_routing_driver.py -> build/lib/neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv
copying neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv/cisco_csr1kv_snippets.py -> build/lib/neutron/plugins/cisco/cfg_agent/device_drivers/csr1kv
creating build/lib/neutron/plugins/embrane
creating build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/__init__.py -> build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/constants.py -> build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/config.py -> build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/contexts.py -> build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/exceptions.py -> build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/utils.py -> build/lib/neutron/plugins/embrane/common
copying neutron/plugins/embrane/common/operation.py -> build/lib/neutron/plugins/embrane/common
creating build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_restproxy_agent.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/__init__.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_agent_scheduler.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_base.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_router_db.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_capabilities.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_servermanager.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_ssl.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/fake_server.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_restproxy_plugin.py -> build/lib/neutron/tests/unit/bigswitch
copying neutron/tests/unit/bigswitch/test_security_groups.py -> build/lib/neutron/tests/unit/bigswitch
creating build/lib/neutron/plugins/cisco/cfg_agent/service_helpers
copying neutron/plugins/cisco/cfg_agent/service_helpers/__init__.py -> build/lib/neutron/plugins/cisco/cfg_agent/service_helpers
copying neutron/plugins/cisco/cfg_agent/service_helpers/routing_svc_helper.py -> build/lib/neutron/plugins/cisco/cfg_agent/service_helpers
creating build/lib/neutron/tests/unit/services/vpn
copying neutron/tests/unit/services/vpn/__init__.py -> build/lib/neutron/tests/unit/services/vpn
copying neutron/tests/unit/services/vpn/test_vpnaas_extension.py -> build/lib/neutron/tests/unit/services/vpn
copying neutron/tests/unit/services/vpn/test_vpn_agent.py -> build/lib/neutron/tests/unit/services/vpn
copying neutron/tests/unit/services/vpn/test_vpnaas_driver_plugin.py -> build/lib/neutron/tests/unit/services/vpn
creating build/lib/neutron/plugins/ml2/drivers/brocade/db
copying neutron/plugins/ml2/drivers/brocade/db/__init__.py -> build/lib/neutron/plugins/ml2/drivers/brocade/db
copying neutron/plugins/ml2/drivers/brocade/db/models.py -> build/lib/neutron/plugins/ml2/drivers/brocade/db
creating build/lib/neutron/plugins/bigswitch
creating build/lib/neutron/plugins/bigswitch/db
copying neutron/plugins/bigswitch/db/porttracker_db.py -> build/lib/neutron/plugins/bigswitch/db
copying neutron/plugins/bigswitch/db/__init__.py -> build/lib/neutron/plugins/bigswitch/db
copying neutron/plugins/bigswitch/db/consistency_db.py -> build/lib/neutron/plugins/bigswitch/db
creating build/lib/neutron/plugins/embrane/l2base
copying neutron/plugins/embrane/l2base/__init__.py -> build/lib/neutron/plugins/embrane/l2base
copying neutron/plugins/embrane/l2base/support_base.py -> build/lib/neutron/plugins/embrane/l2base
copying neutron/plugins/embrane/l2base/support_exceptions.py -> build/lib/neutron/plugins/embrane/l2base
copying neutron/db/l3_dvr_db.py -> build/lib/neutron/db
copying neutron/db/external_net_db.py -> build/lib/neutron/db
copying neutron/db/common_db_mixin.py -> build/lib/neutron/db
copying neutron/db/__init__.py -> build/lib/neutron/db
copying neutron/db/l3_dvrscheduler_db.py -> build/lib/neutron/db
copying neutron/db/l3_hascheduler_db.py -> build/lib/neutron/db
copying neutron/db/servicetype_db.py -> build/lib/neutron/db
copying neutron/db/extraroute_db.py -> build/lib/neutron/db
copying neutron/db/securitygroups_rpc_base.py -> build/lib/neutron/db
copying neutron/db/quota_db.py -> build/lib/neutron/db
copying neutron/db/portsecurity_db.py -> build/lib/neutron/db
copying neutron/db/l3_attrs_db.py -> build/lib/neutron/db
copying neutron/db/l3_gwmode_db.py -> build/lib/neutron/db
copying neutron/db/routerservicetype_db.py -> build/lib/neutron/db
copying neutron/db/api.py -> build/lib/neutron/db
copying neutron/db/l3_hamode_db.py -> build/lib/neutron/db
copying neutron/db/securitygroups_db.py -> build/lib/neutron/db
copying neutron/db/portbindings_db.py -> build/lib/neutron/db
copying neutron/db/l3_agentschedulers_db.py -> build/lib/neutron/db
copying neutron/db/agents_db.py -> build/lib/neutron/db
copying neutron/db/model_base.py -> build/lib/neutron/db
copying neutron/db/db_base_plugin_v2.py -> build/lib/neutron/db
copying neutron/db/dvr_mac_db.py -> build/lib/neutron/db
copying neutron/db/allowedaddresspairs_db.py -> build/lib/neutron/db
copying neutron/db/sqlalchemyutils.py -> build/lib/neutron/db
copying neutron/db/routedserviceinsertion_db.py -> build/lib/neutron/db
copying neutron/db/agentschedulers_db.py -> build/lib/neutron/db
copying neutron/db/extradhcpopt_db.py -> build/lib/neutron/db
copying neutron/db/portbindings_base.py -> build/lib/neutron/db
copying neutron/db/models_v2.py -> build/lib/neutron/db
copying neutron/db/l3_db.py -> build/lib/neutron/db
creating build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/__init__.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_router.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_l2gateway.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_queue.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_versioning.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_lsn.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_secgroup.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/test_switch.py -> build/lib/neutron/tests/unit/vmware/nsxlib
copying neutron/tests/unit/vmware/nsxlib/base.py -> build/lib/neutron/tests/unit/vmware/nsxlib
creating build/lib/neutron/plugins/cisco/db
copying neutron/plugins/cisco/db/__init__.py -> build/lib/neutron/plugins/cisco/db
copying neutron/plugins/cisco/db/network_db_v2.py -> build/lib/neutron/plugins/cisco/db
copying neutron/plugins/cisco/db/n1kv_models_v2.py -> build/lib/neutron/plugins/cisco/db
copying neutron/plugins/cisco/db/n1kv_db_v2.py -> build/lib/neutron/plugins/cisco/db
copying neutron/plugins/cisco/db/network_models_v2.py -> build/lib/neutron/plugins/cisco/db
copying neutron/tests/unit/services/loadbalancer/drivers/__init__.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers
copying neutron/tests/unit/services/loadbalancer/drivers/test_agent_driver_base.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers
creating build/lib/neutron/plugins/brocade
creating build/lib/neutron/plugins/brocade/db
copying neutron/plugins/brocade/db/__init__.py -> build/lib/neutron/plugins/brocade/db
copying neutron/plugins/brocade/db/models.py -> build/lib/neutron/plugins/brocade/db
copying neutron/plugins/nuage/__init__.py -> build/lib/neutron/plugins/nuage
copying neutron/plugins/nuage/nuage_models.py -> build/lib/neutron/plugins/nuage
copying neutron/plugins/nuage/plugin.py -> build/lib/neutron/plugins/nuage
copying neutron/plugins/nuage/syncmanager.py -> build/lib/neutron/plugins/nuage
copying neutron/plugins/nuage/nuagedb.py -> build/lib/neutron/plugins/nuage
creating build/lib/neutron/tests/unit/plumgrid
creating build/lib/neutron/tests/unit/plumgrid/extensions
copying neutron/tests/unit/plumgrid/extensions/__init__.py -> build/lib/neutron/tests/unit/plumgrid/extensions
copying neutron/tests/unit/plumgrid/extensions/test_securitygroups.py -> build/lib/neutron/tests/unit/plumgrid/extensions
creating build/lib/neutron/tests/unit/sriovnicagent
copying neutron/tests/unit/sriovnicagent/test_sriov_neutron_agent.py -> build/lib/neutron/tests/unit/sriovnicagent
copying neutron/tests/unit/sriovnicagent/__init__.py -> build/lib/neutron/tests/unit/sriovnicagent
copying neutron/tests/unit/sriovnicagent/test_eswitch_manager.py -> build/lib/neutron/tests/unit/sriovnicagent
copying neutron/tests/unit/sriovnicagent/test_pci_lib.py -> build/lib/neutron/tests/unit/sriovnicagent
copying neutron/tests/unit/sriovnicagent/test_sriov_agent_config.py -> build/lib/neutron/tests/unit/sriovnicagent
creating build/lib/neutron/extensions
copying neutron/extensions/multiprovidernet.py -> build/lib/neutron/extensions
copying neutron/extensions/servicetype.py -> build/lib/neutron/extensions
copying neutron/extensions/extra_dhcp_opt.py -> build/lib/neutron/extensions
copying neutron/extensions/__init__.py -> build/lib/neutron/extensions
copying neutron/extensions/flavor.py -> build/lib/neutron/extensions
copying neutron/extensions/l3agentscheduler.py -> build/lib/neutron/extensions
copying neutron/extensions/routerservicetype.py -> build/lib/neutron/extensions
copying neutron/extensions/vpnaas.py -> build/lib/neutron/extensions
copying neutron/extensions/dhcpagentscheduler.py -> build/lib/neutron/extensions
copying neutron/extensions/external_net.py -> build/lib/neutron/extensions
copying neutron/extensions/securitygroup.py -> build/lib/neutron/extensions
copying neutron/extensions/quotasv2.py -> build/lib/neutron/extensions
copying neutron/extensions/dvr.py -> build/lib/neutron/extensions
copying neutron/extensions/extraroute.py -> build/lib/neutron/extensions
copying neutron/extensions/lbaas_agentscheduler.py -> build/lib/neutron/extensions
copying neutron/extensions/metering.py -> build/lib/neutron/extensions
copying neutron/extensions/portsecurity.py -> build/lib/neutron/extensions
copying neutron/extensions/loadbalancer.py -> build/lib/neutron/extensions
copying neutron/extensions/portbindings.py -> build/lib/neutron/extensions
copying neutron/extensions/allowedaddresspairs.py -> build/lib/neutron/extensions
copying neutron/extensions/l3.py -> build/lib/neutron/extensions
copying neutron/extensions/l3_ext_gw_mode.py -> build/lib/neutron/extensions
copying neutron/extensions/agent.py -> build/lib/neutron/extensions
copying neutron/extensions/routedserviceinsertion.py -> build/lib/neutron/extensions
copying neutron/extensions/firewall.py -> build/lib/neutron/extensions
copying neutron/extensions/l3_ext_ha_mode.py -> build/lib/neutron/extensions
copying neutron/extensions/providernet.py -> build/lib/neutron/extensions
creating build/lib/neutron/tests/unit/ml2/drivers/arista
copying neutron/tests/unit/ml2/drivers/arista/__init__.py -> build/lib/neutron/tests/unit/ml2/drivers/arista
copying neutron/tests/unit/ml2/drivers/arista/test_arista_mechanism_driver.py -> build/lib/neutron/tests/unit/ml2/drivers/arista
copying neutron/tests/unit/ml2/drivers/arista/test_arista_l3_driver.py -> build/lib/neutron/tests/unit/ml2/drivers/arista
creating build/lib/neutron/plugins/linuxbridge/agent
copying neutron/plugins/linuxbridge/agent/__init__.py -> build/lib/neutron/plugins/linuxbridge/agent
copying neutron/plugins/linuxbridge/agent/linuxbridge_neutron_agent.py -> build/lib/neutron/plugins/linuxbridge/agent
creating build/lib/neutron/plugins/ml2/drivers/l2pop
copying neutron/plugins/ml2/drivers/l2pop/__init__.py -> build/lib/neutron/plugins/ml2/drivers/l2pop
copying neutron/plugins/ml2/drivers/l2pop/mech_driver.py -> build/lib/neutron/plugins/ml2/drivers/l2pop
copying neutron/plugins/ml2/drivers/l2pop/constants.py -> build/lib/neutron/plugins/ml2/drivers/l2pop
copying neutron/plugins/ml2/drivers/l2pop/rpc.py -> build/lib/neutron/plugins/ml2/drivers/l2pop
copying neutron/plugins/ml2/drivers/l2pop/config.py -> build/lib/neutron/plugins/ml2/drivers/l2pop
copying neutron/plugins/ml2/drivers/l2pop/db.py -> build/lib/neutron/plugins/ml2/drivers/l2pop
creating build/lib/neutron/plugins/hyperv
copying neutron/plugins/hyperv/hyperv_neutron_plugin.py -> build/lib/neutron/plugins/hyperv
copying neutron/plugins/hyperv/__init__.py -> build/lib/neutron/plugins/hyperv
copying neutron/plugins/hyperv/agent_notifier_api.py -> build/lib/neutron/plugins/hyperv
copying neutron/plugins/hyperv/model.py -> build/lib/neutron/plugins/hyperv
copying neutron/plugins/hyperv/rpc_callbacks.py -> build/lib/neutron/plugins/hyperv
copying neutron/plugins/hyperv/db.py -> build/lib/neutron/plugins/hyperv
copying neutron/plugins/ml2/driver_api.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/__init__.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/plugin.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/driver_context.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/rpc.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/config.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/db.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/models.py -> build/lib/neutron/plugins/ml2
copying neutron/plugins/ml2/managers.py -> build/lib/neutron/plugins/ml2
creating build/lib/neutron/plugins/ml2/drivers/brocade/nos
copying neutron/plugins/ml2/drivers/brocade/nos/__init__.py -> build/lib/neutron/plugins/ml2/drivers/brocade/nos
copying neutron/plugins/ml2/drivers/brocade/nos/nctemplates.py -> build/lib/neutron/plugins/ml2/drivers/brocade/nos
copying neutron/plugins/ml2/drivers/brocade/nos/nosdriver.py -> build/lib/neutron/plugins/ml2/drivers/brocade/nos
creating build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/test_hyperv_neutron_agent.py -> build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/__init__.py -> build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/test_hyperv_security_groups_driver.py -> build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/test_hyperv_rpcapi.py -> build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/test_hyperv_neutron_plugin.py -> build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/test_hyperv_utilsv2.py -> build/lib/neutron/tests/unit/hyperv
copying neutron/tests/unit/hyperv/test_hyperv_utilsfactory.py -> build/lib/neutron/tests/unit/hyperv
creating build/lib/neutron/tests/functional/agent
creating build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/simple_daemon.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_keepalived.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/__init__.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_iptables.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_ip_lib.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/pinger.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_process_monitor.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_ipset.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_ovsdb_monitor.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/test_async_process.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/tests/functional/agent/linux/base.py -> build/lib/neutron/tests/functional/agent/linux
copying neutron/plugins/ml2/drivers/mechanism_odl.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/mech_ofagent.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/__init__.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/type_tunnel.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/mech_hyperv.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/type_gre.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/mech_linuxbridge.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/mech_openvswitch.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/type_vlan.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/helpers.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/type_local.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/mechanism_ncs.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/type_flat.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/mech_agent.py -> build/lib/neutron/plugins/ml2/drivers
copying neutron/plugins/ml2/drivers/type_vxlan.py -> build/lib/neutron/plugins/ml2/drivers
creating build/lib/neutron/plugins/mlnx/common
copying neutron/plugins/mlnx/common/__init__.py -> build/lib/neutron/plugins/mlnx/common
copying neutron/plugins/mlnx/common/comm_utils.py -> build/lib/neutron/plugins/mlnx/common
copying neutron/plugins/mlnx/common/constants.py -> build/lib/neutron/plugins/mlnx/common
copying neutron/plugins/mlnx/common/config.py -> build/lib/neutron/plugins/mlnx/common
copying neutron/plugins/mlnx/common/exceptions.py -> build/lib/neutron/plugins/mlnx/common
creating build/lib/neutron/tests/unit/nuage
copying neutron/tests/unit/nuage/__init__.py -> build/lib/neutron/tests/unit/nuage
copying neutron/tests/unit/nuage/test_netpartition.py -> build/lib/neutron/tests/unit/nuage
copying neutron/tests/unit/nuage/fake_nuageclient.py -> build/lib/neutron/tests/unit/nuage
copying neutron/tests/unit/nuage/test_syncmanager.py -> build/lib/neutron/tests/unit/nuage
copying neutron/tests/unit/nuage/test_nuage_plugin.py -> build/lib/neutron/tests/unit/nuage
creating build/lib/neutron/api/views
copying neutron/api/views/__init__.py -> build/lib/neutron/api/views
copying neutron/api/views/versions.py -> build/lib/neutron/api/views
creating build/lib/neutron/agent/metadata
copying neutron/agent/metadata/__init__.py -> build/lib/neutron/agent/metadata
copying neutron/agent/metadata/namespace_proxy.py -> build/lib/neutron/agent/metadata
copying neutron/agent/metadata/agent.py -> build/lib/neutron/agent/metadata
creating build/lib/neutron/plugins/ryu/db
copying neutron/plugins/ryu/db/__init__.py -> build/lib/neutron/plugins/ryu/db
copying neutron/plugins/ryu/db/api_v2.py -> build/lib/neutron/plugins/ryu/db
copying neutron/plugins/ryu/db/models_v2.py -> build/lib/neutron/plugins/ryu/db
creating build/lib/neutron/plugins/embrane/agent
copying neutron/plugins/embrane/agent/dispatcher.py -> build/lib/neutron/plugins/embrane/agent
copying neutron/plugins/embrane/agent/__init__.py -> build/lib/neutron/plugins/embrane/agent
creating build/lib/neutron/tests/unit/brocade
copying neutron/tests/unit/brocade/test_brocade_vlan.py -> build/lib/neutron/tests/unit/brocade
copying neutron/tests/unit/brocade/__init__.py -> build/lib/neutron/tests/unit/brocade
copying neutron/tests/unit/brocade/test_brocade_plugin.py -> build/lib/neutron/tests/unit/brocade
copying neutron/tests/unit/brocade/test_brocade_db.py -> build/lib/neutron/tests/unit/brocade
creating build/lib/neutron/tests/unit/api
creating build/lib/neutron/tests/unit/api/rpc
copying neutron/tests/unit/api/rpc/__init__.py -> build/lib/neutron/tests/unit/api/rpc
creating build/lib/neutron/tests/functional/sanity
copying neutron/tests/functional/sanity/__init__.py -> build/lib/neutron/tests/functional/sanity
copying neutron/tests/functional/sanity/test_sanity.py -> build/lib/neutron/tests/functional/sanity
copying neutron/plugins/brocade/vlanbm.py -> build/lib/neutron/plugins/brocade
copying neutron/plugins/brocade/__init__.py -> build/lib/neutron/plugins/brocade
copying neutron/plugins/brocade/NeutronPlugin.py -> build/lib/neutron/plugins/brocade
creating build/lib/neutron/plugins/cisco/l3/rpc
copying neutron/plugins/cisco/l3/rpc/__init__.py -> build/lib/neutron/plugins/cisco/l3/rpc
copying neutron/plugins/cisco/l3/rpc/l3_router_cfgagent_rpc_cb.py -> build/lib/neutron/plugins/cisco/l3/rpc
copying neutron/plugins/cisco/l3/rpc/devices_cfgagent_rpc_cb.py -> build/lib/neutron/plugins/cisco/l3/rpc
copying neutron/plugins/cisco/l3/rpc/l3_router_rpc_joint_agent_api.py -> build/lib/neutron/plugins/cisco/l3/rpc
creating build/lib/neutron/tests/unit/db/metering
copying neutron/tests/unit/db/metering/__init__.py -> build/lib/neutron/tests/unit/db/metering
copying neutron/tests/unit/db/metering/test_db_metering.py -> build/lib/neutron/tests/unit/db/metering
copying neutron/tests/functional/agent/__init__.py -> build/lib/neutron/tests/functional/agent
copying neutron/tests/functional/agent/test_l3_agent.py -> build/lib/neutron/tests/functional/agent
copying neutron/services/metering/metering_plugin.py -> build/lib/neutron/services/metering
copying neutron/services/metering/__init__.py -> build/lib/neutron/services/metering
creating build/lib/neutron/cmd
creating build/lib/neutron/cmd/sanity
copying neutron/cmd/sanity/__init__.py -> build/lib/neutron/cmd/sanity
copying neutron/cmd/sanity/checks.py -> build/lib/neutron/cmd/sanity
creating build/lib/neutron/plugins/embrane/plugins
copying neutron/plugins/embrane/plugins/__init__.py -> build/lib/neutron/plugins/embrane/plugins
copying neutron/plugins/embrane/plugins/embrane_ml2_plugin.py -> build/lib/neutron/plugins/embrane/plugins
copying neutron/plugins/embrane/plugins/embrane_fake_plugin.py -> build/lib/neutron/plugins/embrane/plugins
creating build/lib/neutron/plugins/cisco/service_plugins
copying neutron/plugins/cisco/service_plugins/__init__.py -> build/lib/neutron/plugins/cisco/service_plugins
copying neutron/plugins/cisco/service_plugins/cisco_router_plugin.py -> build/lib/neutron/plugins/cisco/service_plugins
copying neutron/tests/unit/test_neutron_context.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_servicetype.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_extended_attribute.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_security_group.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_iptables_firewall.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_linux_dhcp.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_portsecurity.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/__init__.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/dummy_plugin.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_iptables_manager.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_pnet.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_metadata_namespace_proxy.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_api_v2.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_linux_daemon.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/_test_rootwrap_exec.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_agent_netns_cleanup.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extensions.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_api_api_common.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_api_v2_extension.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/_test_extension_portbindings.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_provider_configuration.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_neutron_manager.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_wsgi.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_dhcp_agent.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_ipv6.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_basetestcase.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_quota_ext.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_extradhcpopts.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_auth.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_agent_rpc.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_linux_external_process.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_config.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_linux_interface.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_firewall.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_common_log.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_common_utils.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_agent_config.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_security_groups_rpc.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_policy.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_allowedaddresspairs.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_ext_gw_mode.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_debug_commands.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/testlib_api.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_post_mortem_debug.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_metadata_agent.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_l3_schedulers.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_routerserviceinsertion.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_db_migration.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/testlib_plugin.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_attributes.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_ext_net.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_db_plugin.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_api_v2_resource.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_agent_ext_plugin.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_hacking.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/extension_stubs.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_l3_agent.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_linux_ip_lib.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_extension_extraroute.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_dhcp_scheduler.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_agent_ovs_cleanup.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/database_stubs.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_dhcp_rpc.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_db_plugin_level.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_l3_plugin.py -> build/lib/neutron/tests/unit
copying neutron/tests/unit/test_agent_linux_utils.py -> build/lib/neutron/tests/unit
creating build/lib/neutron/server
copying neutron/server/__init__.py -> build/lib/neutron/server
creating build/lib/neutron/tests/unit/services/firewall/agents/varmour
copying neutron/tests/unit/services/firewall/agents/varmour/__init__.py -> build/lib/neutron/tests/unit/services/firewall/agents/varmour
copying neutron/tests/unit/services/firewall/agents/varmour/test_varmour_router.py -> build/lib/neutron/tests/unit/services/firewall/agents/varmour
creating build/lib/neutron/tests/unit/services/loadbalancer/drivers/haproxy
copying neutron/tests/unit/services/loadbalancer/drivers/haproxy/__init__.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/haproxy
copying neutron/tests/unit/services/loadbalancer/drivers/haproxy/test_namespace_driver.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/haproxy
copying neutron/tests/unit/services/loadbalancer/drivers/haproxy/test_cfg.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/haproxy
creating build/lib/neutron/tests/unit/services/firewall/drivers/linux
copying neutron/tests/unit/services/firewall/drivers/linux/test_iptables_fwaas.py -> build/lib/neutron/tests/unit/services/firewall/drivers/linux
copying neutron/tests/unit/services/firewall/drivers/linux/__init__.py -> build/lib/neutron/tests/unit/services/firewall/drivers/linux
creating build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/__init__.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_router.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_security_group.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_pfc_driver.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_packet_filter.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_agent_scheduler.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/fake_ofc_manager.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_ofc_manager.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_portbindings.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_db.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/stub_ofc_driver.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_config.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_nec_agent.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_nec_plugin.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_utils.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_trema_driver.py -> build/lib/neutron/tests/unit/nec
copying neutron/tests/unit/nec/test_ofc_client.py -> build/lib/neutron/tests/unit/nec
creating build/lib/neutron/tests/unit/services/l3_router
copying neutron/tests/unit/services/l3_router/__init__.py -> build/lib/neutron/tests/unit/services/l3_router
copying neutron/tests/unit/services/l3_router/test_l3_apic_plugin.py -> build/lib/neutron/tests/unit/services/l3_router
copying neutron/plugins/oneconvergence/__init__.py -> build/lib/neutron/plugins/oneconvergence
copying neutron/plugins/oneconvergence/plugin.py -> build/lib/neutron/plugins/oneconvergence
creating build/lib/neutron/services/loadbalancer/drivers/netscaler
copying neutron/services/loadbalancer/drivers/netscaler/__init__.py -> build/lib/neutron/services/loadbalancer/drivers/netscaler
copying neutron/services/loadbalancer/drivers/netscaler/netscaler_driver.py -> build/lib/neutron/services/loadbalancer/drivers/netscaler
copying neutron/services/loadbalancer/drivers/netscaler/ncc_client.py -> build/lib/neutron/services/loadbalancer/drivers/netscaler
creating build/lib/neutron/plugins/bigswitch/tests
copying neutron/plugins/bigswitch/tests/__init__.py -> build/lib/neutron/plugins/bigswitch/tests
copying neutron/plugins/bigswitch/tests/test_server.py -> build/lib/neutron/plugins/bigswitch/tests
copying neutron/services/metering/drivers/__init__.py -> build/lib/neutron/services/metering/drivers
copying neutron/services/metering/drivers/abstract_driver.py -> build/lib/neutron/services/metering/drivers
creating build/lib/neutron/plugins/bigswitch/agent
copying neutron/plugins/bigswitch/agent/__init__.py -> build/lib/neutron/plugins/bigswitch/agent
copying neutron/plugins/bigswitch/agent/restproxy_agent.py -> build/lib/neutron/plugins/bigswitch/agent
copying neutron/tests/unit/services/firewall/__init__.py -> build/lib/neutron/tests/unit/services/firewall
copying neutron/tests/unit/services/firewall/test_fwaas_plugin.py -> build/lib/neutron/tests/unit/services/firewall
creating build/lib/neutron/services/loadbalancer/drivers/a10networks
copying neutron/services/loadbalancer/drivers/a10networks/__init__.py -> build/lib/neutron/services/loadbalancer/drivers/a10networks
copying neutron/services/loadbalancer/drivers/a10networks/driver_v1.py -> build/lib/neutron/services/loadbalancer/drivers/a10networks
creating build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/test_maclearning.py -> build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/__init__.py -> build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/test_portsecurity.py -> build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/test_providernet.py -> build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/test_networkgw.py -> build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/test_addresspairs.py -> build/lib/neutron/tests/unit/vmware/extensions
copying neutron/tests/unit/vmware/extensions/test_qosqueues.py -> build/lib/neutron/tests/unit/vmware/extensions
creating build/lib/neutron/tests/unit/openvswitch
copying neutron/tests/unit/openvswitch/__init__.py -> build/lib/neutron/tests/unit/openvswitch
copying neutron/tests/unit/openvswitch/test_agent_scheduler.py -> build/lib/neutron/tests/unit/openvswitch
copying neutron/tests/unit/openvswitch/test_ovs_neutron_agent.py -> build/lib/neutron/tests/unit/openvswitch
copying neutron/tests/unit/openvswitch/test_ovs_defaults.py -> build/lib/neutron/tests/unit/openvswitch
copying neutron/tests/unit/openvswitch/test_ovs_tunnel.py -> build/lib/neutron/tests/unit/openvswitch
creating build/lib/neutron/plugins/nec/drivers
copying neutron/plugins/nec/drivers/__init__.py -> build/lib/neutron/plugins/nec/drivers
copying neutron/plugins/nec/drivers/pfc.py -> build/lib/neutron/plugins/nec/drivers
copying neutron/plugins/nec/drivers/trema.py -> build/lib/neutron/plugins/nec/drivers
copying neutron/tests/unit/api/__init__.py -> build/lib/neutron/tests/unit/api
creating build/lib/neutron/tests/unit/notifiers
copying neutron/tests/unit/notifiers/__init__.py -> build/lib/neutron/tests/unit/notifiers
copying neutron/tests/unit/notifiers/test_notifiers_nova.py -> build/lib/neutron/tests/unit/notifiers
creating build/lib/neutron/tests/unit/embrane
copying neutron/tests/unit/embrane/__init__.py -> build/lib/neutron/tests/unit/embrane
copying neutron/tests/unit/embrane/test_embrane_defaults.py -> build/lib/neutron/tests/unit/embrane
copying neutron/tests/unit/embrane/test_embrane_l3_plugin.py -> build/lib/neutron/tests/unit/embrane
copying neutron/tests/unit/embrane/test_embrane_neutron_plugin.py -> build/lib/neutron/tests/unit/embrane
creating build/lib/neutron/tests/unit/extensions
copying neutron/tests/unit/extensions/v2attributes.py -> build/lib/neutron/tests/unit/extensions
copying neutron/tests/unit/extensions/__init__.py -> build/lib/neutron/tests/unit/extensions
copying neutron/tests/unit/extensions/extensionattribute.py -> build/lib/neutron/tests/unit/extensions
copying neutron/tests/unit/extensions/foxinsocks.py -> build/lib/neutron/tests/unit/extensions
copying neutron/tests/unit/extensions/extendedattribute.py -> build/lib/neutron/tests/unit/extensions
creating build/lib/neutron/plugins/brocade/nos
copying neutron/plugins/brocade/nos/__init__.py -> build/lib/neutron/plugins/brocade/nos
copying neutron/plugins/brocade/nos/fake_nosdriver.py -> build/lib/neutron/plugins/brocade/nos
copying neutron/plugins/brocade/nos/nctemplates.py -> build/lib/neutron/plugins/brocade/nos
copying neutron/plugins/brocade/nos/nosdriver.py -> build/lib/neutron/plugins/brocade/nos
creating build/lib/neutron/tests/unit/db/vpn
copying neutron/tests/unit/db/vpn/__init__.py -> build/lib/neutron/tests/unit/db/vpn
copying neutron/tests/unit/db/vpn/test_db_vpnaas.py -> build/lib/neutron/tests/unit/db/vpn
creating build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/l2gateway.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/__init__.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/secgroup.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/router.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/versioning.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/lsn.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/switch.py -> build/lib/neutron/plugins/vmware/nsxlib
copying neutron/plugins/vmware/nsxlib/queue.py -> build/lib/neutron/plugins/vmware/nsxlib
creating build/lib/neutron/services/vpn/device_drivers
copying neutron/services/vpn/device_drivers/__init__.py -> build/lib/neutron/services/vpn/device_drivers
copying neutron/services/vpn/device_drivers/ipsec.py -> build/lib/neutron/services/vpn/device_drivers
copying neutron/services/vpn/device_drivers/cisco_csr_rest_client.py -> build/lib/neutron/services/vpn/device_drivers
copying neutron/services/vpn/device_drivers/cisco_ipsec.py -> build/lib/neutron/services/vpn/device_drivers
creating build/lib/neutron/plugins/linuxbridge/common
copying neutron/plugins/linuxbridge/common/__init__.py -> build/lib/neutron/plugins/linuxbridge/common
copying neutron/plugins/linuxbridge/common/constants.py -> build/lib/neutron/plugins/linuxbridge/common
copying neutron/plugins/linuxbridge/common/config.py -> build/lib/neutron/plugins/linuxbridge/common
creating build/lib/neutron/plugins/midonet/agent
copying neutron/plugins/midonet/agent/__init__.py -> build/lib/neutron/plugins/midonet/agent
copying neutron/plugins/midonet/agent/midonet_driver.py -> build/lib/neutron/plugins/midonet/agent
creating build/lib/neutron/plugins/plumgrid
creating build/lib/neutron/plugins/plumgrid/common
copying neutron/plugins/plumgrid/common/__init__.py -> build/lib/neutron/plugins/plumgrid/common
copying neutron/plugins/plumgrid/common/exceptions.py -> build/lib/neutron/plugins/plumgrid/common
creating build/lib/neutron/services/loadbalancer/drivers/logging_noop
copying neutron/services/loadbalancer/drivers/logging_noop/driver.py -> build/lib/neutron/services/loadbalancer/drivers/logging_noop
copying neutron/services/loadbalancer/drivers/logging_noop/__init__.py -> build/lib/neutron/services/loadbalancer/drivers/logging_noop
creating build/lib/neutron/plugins/openvswitch/agent
copying neutron/plugins/openvswitch/agent/__init__.py -> build/lib/neutron/plugins/openvswitch/agent
copying neutron/plugins/openvswitch/agent/ovs_neutron_agent.py -> build/lib/neutron/plugins/openvswitch/agent
copying neutron/plugins/openvswitch/agent/ovs_dvr_neutron_agent.py -> build/lib/neutron/plugins/openvswitch/agent
creating build/lib/neutron/db/firewall
copying neutron/db/firewall/__init__.py -> build/lib/neutron/db/firewall
copying neutron/db/firewall/firewall_db.py -> build/lib/neutron/db/firewall
creating build/lib/neutron/openstack
creating build/lib/neutron/openstack/common
creating build/lib/neutron/openstack/common/cache
copying neutron/openstack/common/cache/__init__.py -> build/lib/neutron/openstack/common/cache
copying neutron/openstack/common/cache/cache.py -> build/lib/neutron/openstack/common/cache
copying neutron/openstack/common/cache/backends.py -> build/lib/neutron/openstack/common/cache
creating build/lib/neutron/tests/unit/services/loadbalancer/drivers/netscaler
copying neutron/tests/unit/services/loadbalancer/drivers/netscaler/__init__.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/netscaler
copying neutron/tests/unit/services/loadbalancer/drivers/netscaler/test_ncc_client.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/netscaler
copying neutron/tests/unit/services/loadbalancer/drivers/netscaler/test_netscaler_driver.py -> build/lib/neutron/tests/unit/services/loadbalancer/drivers/netscaler
copying neutron/services/l3_router/__init__.py -> build/lib/neutron/services/l3_router
copying neutron/services/l3_router/l3_router_plugin.py -> build/lib/neutron/services/l3_router
copying neutron/services/l3_router/l3_apic.py -> build/lib/neutron/services/l3_router
copying neutron/services/l3_router/l3_arista.py -> build/lib/neutron/services/l3_router
copying neutron/plugins/cisco/__init__.py -> build/lib/neutron/plugins/cisco
copying neutron/plugins/cisco/l2device_plugin_base.py -> build/lib/neutron/plugins/cisco
copying neutron/plugins/cisco/network_plugin.py -> build/lib/neutron/plugins/cisco
creating build/lib/neutron/plugins/openvswitch/common
copying neutron/plugins/openvswitch/common/__init__.py -> build/lib/neutron/plugins/openvswitch/common
copying neutron/plugins/openvswitch/common/constants.py -> build/lib/neutron/plugins/openvswitch/common
copying neutron/plugins/openvswitch/common/config.py -> build/lib/neutron/plugins/openvswitch/common
copying neutron/tests/unit/plumgrid/__init__.py -> build/lib/neutron/tests/unit/plumgrid
copying neutron/tests/unit/plumgrid/test_plumgrid_plugin.py -> build/lib/neutron/tests/unit/plumgrid
creating build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/networkgw_db.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/__init__.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/lsn_db.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/qos_db.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/servicerouter.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/db.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/vcns_models.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/vcns_db.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/models.py -> build/lib/neutron/plugins/vmware/dbexts
copying neutron/plugins/vmware/dbexts/maclearning.py -> build/lib/neutron/plugins/vmware/dbexts
creating build/lib/neutron/plugins/cisco/db/l3
copying neutron/plugins/cisco/db/l3/device_handling_db.py -> build/lib/neutron/plugins/cisco/db/l3
copying neutron/plugins/cisco/db/l3/__init__.py -> build/lib/neutron/plugins/cisco/db/l3
copying neutron/plugins/cisco/db/l3/l3_models.py -> build/lib/neutron/plugins/cisco/db/l3
copying neutron/plugins/cisco/db/l3/l3_router_appliance_db.py -> build/lib/neutron/plugins/cisco/db/l3
creating build/lib/neutron/plugins/metaplugin
creating build/lib/neutron/plugins/metaplugin/common
copying neutron/plugins/metaplugin/common/__init__.py -> build/lib/neutron/plugins/metaplugin/common
copying neutron/plugins/metaplugin/common/config.py -> build/lib/neutron/plugins/metaplugin/common
creating build/lib/neutron/db/migration/models
copying neutron/db/migration/models/__init__.py -> build/lib/neutron/db/migration/models
copying neutron/db/migration/models/head.py -> build/lib/neutron/db/migration/models
copying neutron/db/migration/models/frozen.py -> build/lib/neutron/db/migration/models
creating build/lib/neutron/plugins/nec/extensions
copying neutron/plugins/nec/extensions/__init__.py -> build/lib/neutron/plugins/nec/extensions
copying neutron/plugins/nec/extensions/router_provider.py -> build/lib/neutron/plugins/nec/extensions
copying neutron/plugins/nec/extensions/packetfilter.py -> build/lib/neutron/plugins/nec/extensions
creating build/lib/neutron/notifiers
copying neutron/notifiers/__init__.py -> build/lib/neutron/notifiers
copying neutron/notifiers/nova.py -> build/lib/neutron/notifiers
creating build/lib/neutron/plugins/nuage/extensions
copying neutron/plugins/nuage/extensions/__init__.py -> build/lib/neutron/plugins/nuage/extensions
copying neutron/plugins/nuage/extensions/netpartition.py -> build/lib/neutron/plugins/nuage/extensions
copying neutron/plugins/nuage/extensions/nuage_router.py -> build/lib/neutron/plugins/nuage/extensions
copying neutron/plugins/nuage/extensions/nuage_subnet.py -> build/lib/neutron/plugins/nuage/extensions
creating build/lib/neutron/tests/unit/cisco
creating build/lib/neutron/tests/unit/cisco/n1kv
copying neutron/tests/unit/cisco/n1kv/fake_client.py -> build/lib/neutron/tests/unit/cisco/n1kv
copying neutron/tests/unit/cisco/n1kv/__init__.py -> build/lib/neutron/tests/unit/cisco/n1kv
copying neutron/tests/unit/cisco/n1kv/test_n1kv_db.py -> build/lib/neutron/tests/unit/cisco/n1kv
copying neutron/tests/unit/cisco/n1kv/test_n1kv_plugin.py -> build/lib/neutron/tests/unit/cisco/n1kv
creating build/lib/neutron/tests/unit/metaplugin
copying neutron/tests/unit/metaplugin/__init__.py -> build/lib/neutron/tests/unit/metaplugin
copying neutron/tests/unit/metaplugin/fake_plugin.py -> build/lib/neutron/tests/unit/metaplugin
copying neutron/tests/unit/metaplugin/test_metaplugin.py -> build/lib/neutron/tests/unit/metaplugin
copying neutron/tests/unit/metaplugin/test_basic.py -> build/lib/neutron/tests/unit/metaplugin
copying neutron/plugins/cisco/cfg_agent/device_status.py -> build/lib/neutron/plugins/cisco/cfg_agent
copying neutron/plugins/cisco/cfg_agent/__init__.py -> build/lib/neutron/plugins/cisco/cfg_agent
copying neutron/plugins/cisco/cfg_agent/cfg_exceptions.py -> build/lib/neutron/plugins/cisco/cfg_agent
copying neutron/plugins/cisco/cfg_agent/cfg_agent.py -> build/lib/neutron/plugins/cisco/cfg_agent
creating build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/__init__.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/eventlet_request.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/eventlet_client.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/request.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/client.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/exception.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/version.py -> build/lib/neutron/plugins/vmware/api_client
copying neutron/plugins/vmware/api_client/base.py -> build/lib/neutron/plugins/vmware/api_client
creating build/lib/neutron/tests/unit/services/metering
copying neutron/tests/unit/services/metering/__init__.py -> build/lib/neutron/tests/unit/services/metering
copying neutron/tests/unit/services/metering/test_metering_agent.py -> build/lib/neutron/tests/unit/services/metering
copying neutron/tests/unit/services/metering/test_metering_plugin.py -> build/lib/neutron/tests/unit/services/metering
creating build/lib/neutron/plugins/sriovnicagent
copying neutron/plugins/sriovnicagent/__init__.py -> build/lib/neutron/plugins/sriovnicagent
copying neutron/plugins/sriovnicagent/eswitch_manager.py -> build/lib/neutron/plugins/sriovnicagent
copying neutron/plugins/sriovnicagent/sriov_nic_agent.py -> build/lib/neutron/plugins/sriovnicagent
copying neutron/plugins/sriovnicagent/pci_lib.py -> build/lib/neutron/plugins/sriovnicagent
creating build/lib/neutron/plugins/cisco/models
copying neutron/plugins/cisco/models/__init__.py -> build/lib/neutron/plugins/cisco/models
copying neutron/plugins/cisco/models/virt_phy_sw_v2.py -> build/lib/neutron/plugins/cisco/models
creating build/lib/neutron/tests/unit/ml2/extensions
copying neutron/tests/unit/ml2/extensions/__init__.py -> build/lib/neutron/tests/unit/ml2/extensions
copying neutron/tests/unit/ml2/extensions/test_extension.py -> build/lib/neutron/tests/unit/ml2/extensions
creating build/lib/neutron/tests/unit/cisco/l3
copying neutron/tests/unit/cisco/l3/test_l3_router_appliance_plugin.py -> build/lib/neutron/tests/unit/cisco/l3
copying neutron/tests/unit/cisco/l3/__init__.py -> build/lib/neutron/tests/unit/cisco/l3
copying neutron/tests/unit/cisco/l3/device_handling_test_support.py -> build/lib/neutron/tests/unit/cisco/l3
creating build/lib/neutron/plugins/hyperv/common
copying neutron/plugins/hyperv/common/__init__.py -> build/lib/neutron/plugins/hyperv/common
copying neutron/plugins/hyperv/common/constants.py -> build/lib/neutron/plugins/hyperv/common
creating build/lib/neutron/plugins/embrane/l2base/ml2
copying neutron/plugins/embrane/l2base/ml2/__init__.py -> build/lib/neutron/plugins/embrane/l2base/ml2
copying neutron/plugins/embrane/l2base/ml2/ml2_support.py -> build/lib/neutron/plugins/embrane/l2base/ml2
creating build/lib/neutron/tests/unit/vmware/db
copying neutron/tests/unit/vmware/db/__init__.py -> build/lib/neutron/tests/unit/vmware/db
copying neutron/tests/unit/vmware/db/test_lsn_db.py -> build/lib/neutron/tests/unit/vmware/db
copying neutron/tests/unit/vmware/db/test_nsx_db.py -> build/lib/neutron/tests/unit/vmware/db
creating build/lib/neutron/services/firewall/drivers
copying neutron/services/firewall/drivers/__init__.py -> build/lib/neutron/services/firewall/drivers
copying neutron/services/firewall/drivers/fwaas_base.py -> build/lib/neutron/services/firewall/drivers
creating build/lib/neutron/tests/unit/opencontrail
copying neutron/tests/unit/opencontrail/__init__.py -> build/lib/neutron/tests/unit/opencontrail
copying neutron/tests/unit/opencontrail/test_contrail_plugin.py -> build/lib/neutron/tests/unit/opencontrail
creating build/lib/neutron/plugins/hyperv/agent
copying neutron/plugins/hyperv/agent/__init__.py -> build/lib/neutron/plugins/hyperv/agent
copying neutron/plugins/hyperv/agent/security_groups_driver.py -> build/lib/neutron/plugins/hyperv/agent
copying neutron/plugins/hyperv/agent/utilsfactory.py -> build/lib/neutron/plugins/hyperv/agent
copying neutron/plugins/hyperv/agent/hyperv_neutron_agent.py -> build/lib/neutron/plugins/hyperv/agent
copying neutron/plugins/hyperv/agent/utils.py -> build/lib/neutron/plugins/hyperv/agent
copying neutron/plugins/hyperv/agent/utilsv2.py -> build/lib/neutron/plugins/hyperv/agent
creating build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/__init__.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/nvp_qos.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/servicerouter.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/qos.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/distributedrouter.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/networkgw.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/lsn.py -> build/lib/neutron/plugins/vmware/extensions
copying neutron/plugins/vmware/extensions/maclearning.py -> build/lib/neutron/plugins/vmware/extensions
creating build/lib/neutron/plugins/ml2/drivers/mech_bigswitch
copying neutron/plugins/ml2/drivers/mech_bigswitch/driver.py -> build/lib/neutron/plugins/ml2/drivers/mech_bigswitch
copying neutron/plugins/ml2/drivers/mech_bigswitch/__init__.py -> build/lib/neutron/plugins/ml2/drivers/mech_bigswitch
copying neutron/tests/unit/ml2/drivers/__init__.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/mechanism_logger.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/test_l2population.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/mechanism_test.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/test_mech_mlnx.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/test_bigswitch_mech.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/mechanism_bulkless.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/tests/unit/ml2/drivers/test_ofagent_mech.py -> build/lib/neutron/tests/unit/ml2/drivers
copying neutron/openstack/__init__.py -> build/lib/neutron/openstack
creating build/lib/neutron/plugins/cisco/common
copying neutron/plugins/cisco/common/__init__.py -> build/lib/neutron/plugins/cisco/common
copying neutron/plugins/cisco/common/cisco_constants.py -> build/lib/neutron/plugins/cisco/common
copying neutron/plugins/cisco/common/cisco_exceptions.py -> build/lib/neutron/plugins/cisco/common
copying neutron/plugins/cisco/common/config.py -> build/lib/neutron/plugins/cisco/common
copying neutron/plugins/cisco/common/cisco_faults.py -> build/lib/neutron/plugins/cisco/common
copying neutron/plugins/cisco/common/cisco_credentials_v2.py -> build/lib/neutron/plugins/cisco/common
```



