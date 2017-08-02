# Neutron Ovs Agent RPC 之 `L2populationRpcCallBackTunnelMixin`

## `class L2populationRpcCallBackMixin(object)`

*neutron/plugins/ml2/drivers/l2pop/rpc_manager/l2population_rpc.py*

抽象基类，与 neutron-server mechaism driver l2_population 通信，负责接收 fdb 表的更改信息

### `def add_fdb_entries(self, context, fdb_entries, host=None)`

```
    @log_helpers.log_method_call
    def add_fdb_entries(self, context, fdb_entries, host=None):
        if not host or host == cfg.CONF.host:
            self.fdb_add(context, self._unmarshall_fdb_entries(fdb_entries))
```

### `def remove_fdb_entries(self, context, fdb_entries, host=None)`

```
    @log_helpers.log_method_call
    def remove_fdb_entries(self, context, fdb_entries, host=None):
        if not host or host == cfg.CONF.host:
            self.fdb_remove(context, self._unmarshall_fdb_entries(fdb_entries))
```

### `def update_fdb_entries(self, context, fdb_entries, host=None)`

```
    @log_helpers.log_method_call
    def update_fdb_entries(self, context, fdb_entries, host=None):
        if not host or host == cfg.CONF.host:
            self.fdb_update(context, self._unmarshall_fdb_entries(fdb_entries))
```

### `def _unmarshall_fdb_entries(fdb_entries)`

解析 rpc 接收到的数据

### `def fdb_add(self, context, fdb_entries)`

抽象方法，在 `OVSNeutronAgent` 中实现

### `def fdb_remove(self, context, fdb_entries)`

抽象方法，在 `OVSNeutronAgent` 中实现

### `def fdb_update(self, context, fdb_entries)`

抽象方法，在 `L2populationRpcCallBackTunnelMixin` 中实现

## `class L2populationRpcCallBackTunnelMixin(L2populationRpcCallBackMixin)`

*neutron/plugins/ml2/drivers/l2pop/rpc_manager/l2population_rpc.py*

### `def add_fdb_flow(self, br, port_info, remote_ip, lvm, ofport)`

抽象方法（在 `OVSNeutronAgent` 中实现）。

### `def del_fdb_flow(self, br, port_info, remote_ip, lvm, ofport)`

抽象方法（在 `OVSNeutronAgent` 中实现）。

### `def setup_tunnel_port(self, br, remote_ip, network_type)`

抽象方法（在 `OVSNeutronAgent` 中实现）。

### `def cleanup_tunnel_port(self, br, tun_ofport, tunnel_type)`

抽象方法（在 `OVSNeutronAgent` 中实现）。

### `def setup_entry_for_arp_reply(self, br, action, local_vid, mac_address, ip_address)`

抽象方法（在 `OVSNeutronAgent` 中实现）。

### `def fdb_update(self, context, fdb_entries)`

调用 `_fdb_chg_ip` 方法（在 `OVSNeutronAgent` 中实现）。

### `def _get_lvm_getter(self, local_vlan_map)`


### `def get_agent_ports(self, fdb_entries, local_vlan_map=None)`


### `def fdb_add_tun(self, context, br, lvm, agent_ports, lookup_port)`


### `def fdb_remove_tun(self, context, br, lvm, agent_ports, lookup_port)`

### `def fdb_chg_ip_tun(self, context, br, fdb_entries, local_ip, local_vlan_map=None)`








