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

返回一个方法（为了向后兼容）：

```
        def get_lvm_from_manager(net_id, local_vlan_map):
            vlan_manager = vlanmanager.LocalVlanManager()
            return vlan_manager.get(net_id)
```

### `def get_agent_ports(self, fdb_entries, local_vlan_map=None)`

`local_vlan_map` 是向后兼容使用的，在 O 版本中将被移除。

1. 调用 `_get_lvm_getter` 获取与 fdb entity 中 net id 一致的 lvm（local vlan mapping）
2. 返回 lvm 及其一致的 ports 数据（待更新的）

### `def fdb_add_tun(self, context, br, lvm, agent_ports, lookup_port)`

1. 根据 lvm 中的 network type 和 agent ports 中的 remote ip 获取该 endpoint 在本 l2 agent 上的 vtep
2. 若此 vetp 不存在，则调用 `setup_tunnel_port` （`OVSNeutronAgent` 中实现）创建 vetp
3. 调用 `add_fdb_flow`（`OVSNeutronAgent` 中实现）增加 arp responser 流表

### `def fdb_remove_tun(self, context, br, lvm, agent_ports, lookup_port)`

1. 根据 lvm 中的 network type 和 agent ports 中的 remote ip 获取该 endpoint 在本 l2 agent 上的 vtep
2. 若没有 vtep 则忽略此次操作
3. 调用 `del_fdb_flow` （`OVSNeutronAgent` 中实现）删除与 port 有关的 arp responser 流表以及单播流表
4. 若此 port 是关于 vtep 的消息，则调用 `cleanup_tunnel_port` （`OVSNeutronAgent` 中实现）删除该 vtep（意味着对端的 endpoint 不复存在了）

### `def fdb_chg_ip_tun(self, context, br, fdb_entries, local_ip, local_vlan_map=None)`

1. 调用 `setup_entry_for_arp_reply` （`OVSNeutronAgent` 中实现）增加新的 arp responser 的 flow entity
2. 调用 `setup_entry_for_arp_reply` （`OVSNeutronAgent` 中实现）删除旧的 arp responser 的 flow entity