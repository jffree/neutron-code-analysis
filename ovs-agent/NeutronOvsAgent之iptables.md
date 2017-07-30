# Neutron Ovs Agent 之 iptables

*neutron/agent/linux/iptables_firewall.py*

## `class IptablesFirewallDriver(firewall.FirewallDriver)`

```
    IPTABLES_DIRECTION = {firewall.INGRESS_DIRECTION: 'physdev-out',
                          firewall.EGRESS_DIRECTION: 'physdev-in'}

    def __init__(self, namespace=None):
        self.iptables = iptables_manager.IptablesManager(
            state_less=True,
            use_ipv6=ipv6_utils.is_enabled(),
            namespace=namespace)
        # TODO(majopela, shihanzhang): refactor out ipset to a separate
        # driver composed over this one
        self.ipset = ipset_manager.IpsetManager(namespace=namespace)
        self.ipconntrack = ip_conntrack.IpConntrackManager(
            self.get_device_zone, namespace=namespace)
        self._populate_initial_zone_map()
        # list of port which has security group
        self.filtered_ports = {}
        self.unfiltered_ports = {}
        self._add_fallback_chain_v4v6()
        self._defer_apply = False
        self._pre_defer_filtered_ports = None
        self._pre_defer_unfiltered_ports = None
        # List of security group rules for ports residing on this host
        self.sg_rules = {}
        self.pre_sg_rules = None
        # List of security group member ips for ports residing on this host
        self.sg_members = collections.defaultdict(
            lambda: collections.defaultdict(list))
        self.pre_sg_members = None
        self.enable_ipset = cfg.CONF.SECURITYGROUP.enable_ipset
        self._enabled_netfilter_for_bridges = False
        self.updated_rule_sg_ids = set()
        self.updated_sg_members = set()
        self.devices_with_updated_sg_members = collections.defaultdict(list)
```

















## `class FirewallDriver(object)`

抽象基类。

*neutron/agent/firewall.py*







