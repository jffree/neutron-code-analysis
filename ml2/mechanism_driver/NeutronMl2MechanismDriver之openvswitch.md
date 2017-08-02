# Neutron Ml2 Mechanism Driver 之 openvswitch

*neutron/ml2/drivers/openvswitch/mech_driver/mech_openvswitch.py*

主要实现的是 port binding host

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

### `def try_to_bind_segment_for_agent(self, context, segment, agent)`

1. 调用 `check_segment_for_agent` （`SimpleAgentMechanismDriverBase` 中实现）检查 segment 数据是否符合 agent 的设定
2. 调用 `PortContext.set_binding` 实现 port 的绑定

### `def get_mappings(self, agent)`

```
    def get_mappings(self, agent):
        return agent['configurations'].get('bridge_mappings', {})
```

`bridge_mappings` 是设定值，例如 `{"public": "br-ex"}`

### `def get_allowed_network_types(self, agent)`

获取 ovs agent 支持的网络类型

### `def get_vif_type(self, agent, context)`

获取 vif type（ovs）

### `def get_vif_details(self, agent, context)`

1. 调用 `_pre_get_vif_details` 确定 vif details
2. 调用 `_set_bridge_name` 增加 vif_details 的 bridge_name 属性

### `def _pre_get_vif_details(self, agent, context)`

确定 vif_details

### `def _set_bridge_name(port, vif_details)`

增加 vif_details 的 bridge_name 属性




