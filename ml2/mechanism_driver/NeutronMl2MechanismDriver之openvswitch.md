# Neutron Ml2 Mechanism Driver 之 openvswitch

*neutron/ml2/drivers/openvswitch/mech_driver/mech_openvswitch.py*

## `class OpenvswitchMechanismDriver(mech_agent.SimpleAgentMechanismDriverBase)`

```
    supported_qos_rule_types = [qos_consts.RULE_TYPE_BANDWIDTH_LIMIT,
                                qos_consts.RULE_TYPE_DSCP_MARKING]

    def __init__(self):
        sg_enabled = securitygroups_rpc.is_firewall_enabled()
        hybrid_plug_required = (not cfg.CONF.SECURITYGROUP.firewall_driver or
            cfg.CONF.SECURITYGROUP.firewall_driver in (
                IPTABLES_FW_DRIVER_FULL, 'iptables_hybrid')) and sg_enabled
        vif_details = {portbindings.CAP_PORT_FILTER: sg_enabled,
                       portbindings.OVS_HYBRID_PLUG: hybrid_plug_required}
        super(OpenvswitchMechanismDriver, self).__init__(
            constants.AGENT_TYPE_OVS,
            portbindings.VIF_TYPE_OVS,
            vif_details)
```

1. 调用 `is_firewall_enabled` 检测是否支持 firewall。（这里为 true）
2. 判断 `hybrid_plug_required` 是否为 True（这里为 true）
3. 构造 `vif_details` `{'port_filter':True, 'ovs_hybrid_plug':True}`

### `def check_vlan_transparency(self, context)`

```
    def check_vlan_transparency(self, context):
        """Currently Openvswitch driver doesn't support vlan transparency."""
        return False
```






