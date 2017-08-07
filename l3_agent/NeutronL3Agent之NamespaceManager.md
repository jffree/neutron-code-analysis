# Neuton l3 agent 之 `NamespaceManager`

*neutron/agent/l2/namespace_manager.py*

## `class NamespaceManager(object)`

```
    ns_prefix_to_class_map = {
        namespaces.NS_PREFIX: namespaces.RouterNamespace,
        dvr_snat_ns.SNAT_NS_PREFIX: dvr_snat_ns.SnatNamespace,
        dvr_fip_ns.FIP_NS_PREFIX: dvr_fip_ns.FipNamespace,
    }

    def __init__(self, agent_conf, driver, metadata_driver=None):
        """Initialize the NamespaceManager.

        :param agent_conf: configuration from l3 agent
        :param driver: to perform operations on devices
        :param metadata_driver: used to cleanup stale metadata proxy processes
        """
        self.agent_conf = agent_conf
        self.driver = driver
        self._clean_stale = True
        self.metadata_driver = metadata_driver
        if metadata_driver:
            self.process_monitor = external_process.ProcessMonitor(
                config=agent_conf,
                resource_type='router')
```

初始化了一个 `ProcessMonitor` 实例
