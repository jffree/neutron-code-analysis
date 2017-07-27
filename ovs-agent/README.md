# Neutron OVS agent 的启动

* 在 `setup.cfg` 中可以看到 ovs agent 的启动命令对应：

```
[entry_points]
console_scripts =

    neutron-openvswitch-agent = neutron.cmd.eventlet.plugins.ovs_neutron_agent:main
```

* 在 *neutron/cmd/eventlet/plugins/ovs_neutron_agent.py* 可以看到：

```
import neutron.plugins.ml2.drivers.openvswitch.agent.main as agent_main


def main():
    agent_main.main()
```

* 在 *neutron/plugins/ml2/drivers/openvswitch/agent/main.py* 可以看到：

```
_main_modules = {
    'ovs-ofctl': 'neutron.plugins.ml2.drivers.openvswitch.agent.openflow.'
                 'ovs_ofctl.main',
    'native': 'neutron.plugins.ml2.drivers.openvswitch.agent.openflow.'
                 'native.main',
}

def main():
    common_config.init(sys.argv[1:])
    driver_name = cfg.CONF.OVS.of_interface
    mod_name = _main_modules[driver_name]
    mod = importutils.import_module(mod_name)
    mod.init_config()
    common_config.setup_logging()
    n_utils.log_opt_values(LOG)
    profiler.setup("neutron-ovs-agent", cfg.CONF.host)
    mod.main()
```

* `of_interface` 在 *neutron/plugins/ml2/drivers/openvswitch/agent/common/config.py* 中定义：

```
    cfg.StrOpt('of_interface', default='native',
               choices=['ovs-ofctl', 'native'],
               help=_("OpenFlow interface to use.")),
```

`of_interface` 默认为 native，对应的是 *neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/main.py*

```
cfg.CONF.import_group(
    'OVS',
    'neutron.plugins.ml2.drivers.openvswitch.agent.common.config')


def init_config():
    ryu_cfg.CONF(project='ryu', args=[])
    ryu_cfg.CONF.ofp_listen_host = cfg.CONF.OVS.of_listen_address
    ryu_cfg.CONF.ofp_tcp_listen_port = cfg.CONF.OVS.of_listen_port

def main():
    app_manager.AppManager.run_apps([
        'neutron.plugins.ml2.drivers.openvswitch.agent.'
        'openflow.native.ovs_ryuapp',
    ])
```

`of_listen_address` 在 *neutron/plugins/ml2/drivers/openvswitch/agent/common/config.py* 中定义，默认为 `127.0.0.1`
`of_listen_port` 在 *neutron/plugins/ml2/drivers/openvswitch/agent/common/config.py* 中定义，默认为 `6633`

这两个选项构成了监听 openflow 连接的地址和端口

* 在 *neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/ovs_ryuapp.py* 中，我们发现了真正的 RYU APP：

```
class OVSNeutronAgentRyuApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def start(self):
        # Start Ryu event loop thread
        super(OVSNeutronAgentRyuApp, self).start()

        # patch ryu
        ofproto_v1_3.oxm_types.append(
            oxm_fields.NiciraExtended0('vlan_tci', 4, type_desc.Int2))
        oxm_fields.generate(ofproto_v1_3.__name__)

        def _make_br_cls(br_cls):
            return functools.partial(br_cls, ryu_app=self)

        # Start agent main loop thread
        bridge_classes = {
            'br_int': _make_br_cls(br_int.OVSIntegrationBridge),
            'br_phys': _make_br_cls(br_phys.OVSPhysicalBridge),
            'br_tun': _make_br_cls(br_tun.OVSTunnelBridge),
        }
        return hub.spawn(agent_main_wrapper, bridge_classes)
```

`functools.partial(br_cls, ryu_app=self)` 这句代码的作用是：`br_cls` 在初始化时会自动加上 `ryu_app=self` 这个参数。

* 关于 ryu app，我们先不考虑。我看看到最后一行，这个 ryu app 孵化一个线程，运行 `agent_main_wrapper` 方法

同样在 *neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/ovs_ryuapp.py* 中

```
def agent_main_wrapper(bridge_classes):
    try:
        ovs_agent.main(bridge_classes)
    except Exception:
        LOG.exception(_LE("Agent main thread died of an exception"))
    finally:
        # The following call terminates Ryu's AppManager.run_apps(),
        # which is needed for clean shutdown of an agent process.
        # The close() call must be called in another thread, otherwise
        # it suicides and ends prematurely.
        hub.spawn(app_manager.AppManager.get_instance().close)
```

终于看到关键点：`ovs_agent.main(bridge_classes)`，这才是我们 ovs agent 的真正入口点

* 在 *neutron/plugins/ml2/drivers/openvswitch/agent/ovs_neutron_agent.py* 中

```
def main(bridge_classes):
    prepare_xen_compute()
    ovs_capabilities.register()
    validate_tunnel_config(cfg.CONF.AGENT.tunnel_types, cfg.CONF.OVS.local_ip)

    try:
        agent = OVSNeutronAgent(bridge_classes, cfg.CONF)
        capabilities.notify_init_event(n_const.AGENT_TYPE_OVS, agent)
    except (RuntimeError, ValueError) as e:
        LOG.error(_LE("%s Agent terminated!"), e)
        sys.exit(1)
    agent.daemon_loop()
```

`tunnel_types` 在 ml2_conf.ini 中设定为：`tunnel_types = vxlan`
`local_ip` 在 ml2_conf.ini 中设定为：`local_ip = 172.16.100.126` （本地物理网卡的 ip）

1. `prepare_xen_compute` 判断是否用 xen 来提供计算服务
2. `ovs_capabilities.register` 用来注册一个系统资源的回调监听（resource：`Open vSwitch agent`；callback：`neutron.services.trunk.drivers.openvswitch.agent.driver.init_handler`；event：`after_init`）。
3. `validate_tunnel_config` 用来验证 tunnel 的配置是否正确
4. 创建 `OVSNeutronAgent` 对象
5. 发送 `Open vSwitch agent` 建立的通知，这会调用监听 `Open vSwitch agent` 资源创建的回调方法 `neutron.services.trunk.drivers.openvswitch.agent.driver.init_handler`
6. 调用 `agent.daemon_loop`


* 那么我们可以知道 ovs agent 初始化做了下面的几件事情：
 1. 实例化 `OVSNeutronAgent` 
 2. 通过回调函数 `neutron.services.trunk.drivers.openvswitch.agent.driver.init_handler` 处理 `OVSNeutronAgent` 的初始化
 3. 调用 `agent.daemon_loop` 方法