# Neutron l2 extension manager

*neutron/agent/l2/l2_agent_extension_manager.py*

```
L2_AGENT_EXT_MANAGER_NAMESPACE = 'neutron.agent.l2.extensions'
```

在 setup.cfg 中，我们可以看到：

```
neutron.agent.l2.extensions =
    qos = neutron.agent.l2.extensions.qos:QosAgentExtension
    fdb = neutron.agent.l2.extensions.fdb_population:FdbPopulationAgentExtension
```

## `class L2AgentExtensionsManager(agent_ext_manager.AgentExtensionsManager)`

```
    def __init__(self, conf):
        super(L2AgentExtensionsManager, self).__init__(conf,
                L2_AGENT_EXT_MANAGER_NAMESPACE)
```

在加载完 extension 后，会当有 handle_port、delete_port 发生时，同样会调用 extension 中对应的方法。

```
    def handle_port(self, context, data):
        """Notify all agent extensions to handle port."""
        for extension in self:
            if hasattr(extension.obj, 'handle_port'):
                extension.obj.handle_port(context, data)
            else:
                LOG.error(
                    _LE("Agent Extension '%(name)s' does not "
                        "implement method handle_port"),
                    {'name': extension.name}
                )

    def delete_port(self, context, data):
        """Notify all agent extensions to delete port."""
        for extension in self:
            if hasattr(extension.obj, 'delete_port'):
                extension.obj.delete_port(context, data)
            else:
                LOG.error(
                    _LE("Agent Extension '%(name)s' does not "
                        "implement method delete_port"),
                    {'name': extension.name}
                )
```



## `class AgentExtensionsManager(stevedore.named.NamedExtensionManager)`

这个类没什么，主要是实现 extension 的加载

```
    def __init__(self, conf, namespace):
        super(AgentExtensionsManager, self).__init__(
            namespace, conf.agent.extensions,
            invoke_on_load=True, name_order=True)
        LOG.info(_LI("Loaded agent extensions: %s"), self.names())
```

### `def initialize(self, connection, driver_type, agent_api=None)`

```
    def initialize(self, connection, driver_type, agent_api=None):
        for extension in self:
            LOG.info(_LI("Initializing agent extension '%s'"), extension.name)
            # If the agent has provided an agent_api object, this object will
            # be passed to all interested extensions.  This object must be
            # consumed by each such extension before the extension's
            # intialize() method is called, as the initilization step
            # relies on the agent_api already being available.

            extension.obj.consume_api(agent_api)
            extension.obj.initialize(connection, driver_type)
```

对于这个方法，我拿实例来说明：

* 在 `OVSNeutronAgent.init_extension_manager` 方法中可以看到对本方法的调用。

```
    def init_extension_manager(self, connection):
        ext_manager.register_opts(self.conf)
        self.ext_manager = (
            ext_manager.L2AgentExtensionsManager(self.conf))
        self.agent_api = ovs_ext_api.OVSAgentExtensionAPI(self.int_br,
                                                          self.tun_br)
        self.ext_manager.initialize(
            connection, constants.EXTENSION_DRIVER_TYPE,
            self.agent_api)
```

* 我们假设用到了 l2 qos extension，代码如下：

```
class QosOVSAgentDriver(qos.QosAgentDriver):

    SUPPORTED_RULES = (
        mech_openvswitch.OpenvswitchMechanismDriver.supported_qos_rule_types)

    def __init__(self):
        super(QosOVSAgentDriver, self).__init__()
        self.br_int_name = cfg.CONF.OVS.integration_bridge
        self.br_int = None
        self.agent_api = None
        self.ports = collections.defaultdict(dict)

    def consume_api(self, agent_api):
        self.agent_api = agent_api

    def initialize(self):
        self.br_int = self.agent_api.request_int_br()
        self.cookie = self.br_int.default_cookie
```

这意味着 qos extension 想要对 br-int 上的流表进行操作。

用 cookie 值来区分那个一个 flow entity 是被 qos extension 操作的。