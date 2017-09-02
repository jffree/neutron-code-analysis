# Neutron L3 Agent 之 RouterInfo

*neutron/agent/l3/router_info.py*

## `class RouterInfo(object)`

```
    def __init__(self,
                 router_id,
                 router,
                 agent_conf,
                 interface_driver,
                 use_ipv6=False):
        self.router_id = router_id
        self.ex_gw_port = None
        self._snat_enabled = None
        self.fip_map = {}
        self.internal_ports = []
        self.floating_ips = set()
        # Invoke the setter for establishing initial SNAT action
        self.router = router
        self.use_ipv6 = use_ipv6
        ns = self.create_router_namespace_object(
            router_id, agent_conf, interface_driver, use_ipv6)
        self.router_namespace = ns
        self.ns_name = ns.name
        self.available_mark_ids = set(range(ADDRESS_SCOPE_MARK_ID_MIN,
                                            ADDRESS_SCOPE_MARK_ID_MAX))
        self._address_scope_to_mark_id = {
            DEFAULT_ADDRESS_SCOPE: self.available_mark_ids.pop()}
        self.iptables_manager = iptables_manager.IptablesManager(
            use_ipv6=use_ipv6,
            namespace=self.ns_name)
        self.initialize_address_scope_iptables()
        self.routes = []
        self.agent_conf = agent_conf
        self.driver = interface_driver
        # radvd is a neutron.agent.linux.ra.DaemonMonitor
        self.radvd = None
```
