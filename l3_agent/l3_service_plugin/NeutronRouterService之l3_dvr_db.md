# Neutron Router Service 之 l3_dvr_db

*neutron/db/l3_dvr_db.py*

为 l3 router 增加 dvr 的处理

## `class L3_NAT_with_dvr_db_mixin(l3_db.L3_NAT_db_mixin, l3_attrs_db.ExtraAttributesMixin)`

```
    router_device_owners = (
        l3_db.L3_NAT_db_mixin.router_device_owners +
        (const.DEVICE_OWNER_DVR_INTERFACE,
         const.DEVICE_OWNER_ROUTER_SNAT,
         const.DEVICE_OWNER_AGENT_GW))

    extra_attributes = (
        l3_attrs_db.ExtraAttributesMixin.extra_attributes + [{
            'name': "distributed",
            'default': cfg.CONF.router_distributed
        }])
```

### `def _get_dvr_sync_data(self, context, host, agent, router_ids=None, active=None)`

1. 调用 `L3_NAT_dbonly_mixin._get_router_info_list` 获取与 router_ids 所代表的 router 有关的详细数据（包含 port 和 floating ip）
2. 获取 distributed router 的 id，获取与 distributed router 绑定的 floating ip
3. 若是含有 与 distributed router 绑定的 floating ip，则：
 1. 调用 `core_plugin.get_ports` 获取与这些 floating ip 绑定的 port
 2. 获取那些与该 host 绑定的 port，或者将要迁移到该 host 上的 port
 3. 若是上一步获取的 port绑定了 floating ip
  1. 调用 `_get_dvr_service_port_hostid` 获取提供 dvr 服务的 port 的 host_id 属性
  2. 调用 `_get_dvr_migrating_service_port_hostid` 获取提供 dvr 服务的 port 准备迁移到的 host 的 id
 4. 调用 `_process_routers` 为 router 数据填充 `_snat_router_interfaces` 属性
 5. 调用 `_process_floating_ips_dvr` 为 router 数据填充 `_floatingips` 和 `_floatingip_agent_interfaces` 属性
4. 调用 `L3_NAT_dbonly_mixin._populate_mtu_and_subnets_for_ports` 完善 port 的 subnet 数据和 mtu
5. 调用 `ExtraRoute_dbonly_mixin._process_interfaces` 为 router 增加 `_interfaces` 属性
6. 返回 router 的所有数据

*我觉得这个过程肯定是慢慢丰富起来的，根据 l3 agent 的需求*


### `def _build_routers_list(self, context, routers, gw_ports)`

1. 查询数据库 `RouterL3AgentBinding` 获取所有与 routers 有关的绑定记录
2. 完善各个 router 的数据（添加 `gw_port_id`、`gw_port`、`enable_snat`、`gw_port_host` 属性）

### `def _get_dvr_service_port_hostid(self, context, port_id, port=None)`

若是该 port 是用来提供 dvr 服务的，则返回该 port 的 host_id 属性

### `def _get_dvr_migrating_service_port_hostid(self, context, port_id, port=None)`

若该 port 是用来提供 dvr 服务的，则检查该 port 是否准备迁移到一个 host 上，若是的话则返回该 host 的 Id

### `def _process_routers(self, context, routers)`

1. 调用 `_get_snat_sync_interfaces` 获取用于提供 snat 服务的 port 的数据信息
2. 为所有的 router 数据填充 `_snat_router_interfaces` 属性

### `def _get_snat_sync_interfaces(self, context, router_ids)`

获取用于提供 snat 服务的 port 的数据信息

### `def _process_floating_ips_dvr(self, context, routers_dict, floating_ips, host, agent)`

1. 为 router 添加 `_floatingips` 属性。
 1. 若该 router 为 distributed，则需要判断 floating ip 的 host 属性是否与 `host` 一致
2. 为 router 添加 `_floatingip_agent_interfaces` 属性。
 1. 调用 `_get_fip_sync_interfaces` 获取属于 agent 的 `floatingip_agent_gateway` 的 Port

### `def _get_fip_sync_interfaces(self, context, fip_agent_id)`

获取属于 agent 的 `floatingip_agent_gateway` 的 Port

### `def remove_unbound_allowed_address_pair_port_binding(self, context, service_port_dict, port_address_pairs, address_pair_port=None)`

1. 若是 `address_pair_port` 参数为空，则调用 `_get_address_pair_active_port_with_fip` 是否有 port 与 `address_pair_port` 中的 `ip_address` 绑定
2. 若存在与之绑定的 port，则会调用 `core_plugin.update_port` 更新这个 port 的一些信息（删除该 port 与 service_port 的相关联信息）

* 解析：
 1. port 的 `allowed_address_pairs` 属性可以让 port 有多个 ip 地址，并且这些 ip 地址都可以访问网络
 2. 这种场景常常用于 ha 的部署中

### `def _get_address_pair_active_port_with_fip(self, context, port_dict, port_addr_pair_ip)`

若 port 的 `allowed_address_pairs` 中的 ip_address 是一个 floating ip，则通过调用 `core_plugin.get_port` 获取与该 floating ip 绑定的 port

### `def _get_allowed_address_pair_fixed_ips(self, context, port_dict)`

1. 获取该 port 的 `allowed_address_pairs` 属性
2. 获取 `allowed_address_pairs` 属性中的 `ip_address` 数据
3. 根据 ip address 获取其所在的 subnet

### `def delete_arp_entry_for_dvr_service_port(self, context, port_dict, fixed_ips_to_delete=None)`

1. 调用 `_should_update_arp_entry_for_dvr_service_port` 判断该 prot 需要调整 arp 记录
2. 若 `fixed_ips_to_delete` 不空，则调用 `_get_allowed_address_pair_fixed_ips` 获取 Port 的 `allowed_address_pairs` 以及 port 本身的 ip 作为 `fixed_ips_to_delete`
3. 对于 `fixed_ips_to_delete` 中的记录，调用 `_generate_arp_table_and_notify_agent` 通知 l3 agent 删除 arp 记录

### `def _should_update_arp_entry_for_dvr_service_port(self, port_dict)`

```
    def _should_update_arp_entry_for_dvr_service_port(self, port_dict):
        # Check this is a valid VM or service port
        return (n_utils.is_dvr_serviced(port_dict['device_owner']) and
                port_dict['fixed_ips'])
```

### `def _generate_arp_table_and_notify_agent(self, context, fixed_ip, mac_address, notifier)`

通知 l3 agent 删除相应的 arp 记录

### `def _get_floatingip_on_port(self, context, port_id=None)`

查询数据库 `FloatingIP` 获取该 port 的 floating ip

### `def check_for_fip_and_create_agent_gw_port_on_host_if_not_exists(self, context, port, host)`

1. 调用 `_get_floatingip_on_port` 获取 port 上的 floating ip
2. 调用 `create_fip_agent_gw_port_if_not_exists` 检查该 floating ip 所在网络是否在该 agent 上存在网关，若不存在则创建一个

### `def create_fip_agent_gw_port_if_not_exists(self, context, network_id, host)`

1. 调用 `_get_agent_by_type_and_host` 获取 host 上的 l3 agent 实例
2. 调用 `_get_agent_gw_ports_exist_for_network` 检查 l3 agent 上是否存在为 network 提供网关服务的 port
3. 若有网关 port，调用 `core_plugin.create_port` 创建网关 port
4. 创建网关 port 成功后，调用 `L3_NAT_dbonly_mixin._populate_mtu_and_subnets_for_ports` 完善网关 port 的相关信息
5. 若本来就存在网关 port，同样调用 `L3_NAT_dbonly_mixin._populate_mtu_and_subnets_for_ports` 完善网关 port 的相关信息

### `def _get_agent_gw_ports_exist_for_network(self, context, network_id, host, agent_id)`

检查 l3 agent 上是否存在为 network 提供网关服务的 port

### `def update_unbound_allowed_address_pair_port_binding(self, context, service_port_dict, port_address_pairs, address_pair_port=None)`

1. 若是 `address_pair_port` 参数为空，则调用 `_get_address_pair_active_port_with_fip` 是否有 port 与 `address_pair_port` 中的 `ip_address` 绑定
2. 调用 `core_plugin.update_port` 更新 floating ip 原 port 的数据

### `def update_arp_entry_for_dvr_service_port(self, context, port_dict)`

1. 调用 `_should_update_arp_entry_for_dvr_service_port` 判断该 prot 需要调整 arp 记录
2. 若 `fixed_ips_to_delete` 不空，则调用 `_get_allowed_address_pair_fixed_ips` 获取 Port 的 `allowed_address_pairs` 以及 port 本身的 ip 作为 `fixed_ips_to_delete`
3. 调用 `_generate_arp_table_and_notify_agent` 生成 ARP 数据，并发送 RPC 通知

### `def _create_router_db(self, context, router, tenant_id)`

*重写 `L3_NAT_dbonly_mixin._create_router_db` 方法，增加了处理 dvr 服务的功能*

1. 调用 `L3_NAT_dbonly_mixin._create_router_db` 创建 `Router` 数据库记录
2. 调用 `is_distributed_router` 判断该 router 是否为 distributed router
3. 调用 `_process_extra_attr_router_create` 创建与该 router 相关联的 `RouterExtraAttributes` 数据库记录
4. 返回处理后的 router 数据

### `def _update_router_db(self, context, router_id, data)`

*重写 `L3_NAT_dbonly_mixin._update_router_db` 方法，增加了处理 dvr 服务的功能*

1. 调用 `L3_NAT_dbonly_mixin._update_router_db` 更新 Router 数据库的记录
2. 判断 router 是否由非 distributed 更新为 distributed
3. 调用 `_validate_router_migration` 验证 router 的 distributed 属性转变是否合法
4. 更新 router 的 `extra_attributes` 属性
5. 若更新的数据中 `distributed` 属性为 True 的话，则调用 `L3_NAT_dbonly_mixin._migrate_router_ports` 更新 router 上 port 的 device_owner 为 dvr interface
6. 若 router 是否由非 distributed 更新为 distribute，则:
 1. 若更新后的 router 存在 `gw_port_id` 属性，则调用 `_create_snat_intf_ports_if_not_exists` 获取该 router 上提供 snat 服务的 port，若没有则创建
 2. 调用 `list_l3_agents_hosting_router` 获取与该 router 绑定的 l3 agent 数据，然后调用 `_unbind_router` 将 router 与这些 l3 agent 解除绑定

**两件事：**

1. 每个 router （该 router 含有 gateway port）上有几个 subnet，则会有几个 snat port
2. distributed router 不会与任何的 l3 agent 绑定

### `def _validate_router_migration(self, context, router_db, router_res)`

1. 将一个 distributed router 更新至非 distributed router 是不合法的
2. 只有在 router 的 admin_state_up 属性为 False 的情况下才可以将 router 由非 distributed 转化为 distributed

### `def _create_snat_intf_ports_if_not_exists(self, context, router)`

1. 调用 `_get_snat_interface_ports_for_router` 获取 router 上提供 snat 服务的 port 的数据
2. 若存在提供 snat 服务的 port，则调用 `L3_NAT_dbonly_mixin._populate_mtu_and_subnets_for_ports` 完善网关 port 的相关信息，然后直接退出
3. 若不存在提供 snat 服务的 port：
 1. 获取该 router 是提供 dvr 服务的 port
 2. 调用 `_add_csnat_router_interface_port` 为 router 上所有的子网创建都创建一个提供 snat 服务的 port
 3. 调用 `_populate_mtu_and_subnets_for_ports` 完善新创建的 snat port 的信息

### `def _get_snat_interface_ports_for_router(self, context, router_id)`

查询 `RouterPort` 数据库记录，获取 router 上提供 snat 服务的 port 的数据

### `def _add_csnat_router_interface_port(self, context, router, network_id, subnet_id, do_pop=True)`

1. 调用 `create_port.create_port` 创建一个提供 snat 服务的 port
2. 创建一个提供 snat 服务的 `RouterPort` 数据库记录
3. 调用 `_populate_mtu_and_subnets_for_ports` 完善提供 snat 服务的 port 的信息

### `def _delete_current_gw_port(self, context, router_id, router, new_network)`

1. 获取当前 router 上 gateway Port 所在的 network（也就是该router所绑定的 external network）
2. 调用 `L3_NAT_dbonly_mixin._delete_current_gw_port` 删除 gateway port 数据
3. 若 router 为 distributed router，且 router 的 external network 发生了变化：
 1. 调用 `delete_csnat_router_interface_ports` 删除所有的 snat port
 2. 调用 `core_plugin.get_ports` 获取该 router 的 gateway port
 3. 若不存在属于 external network 的 router gateway port：
  1. 调用 `delete_floatingip_agent_gateway_port` 删除该 host 上的属于该 external network 的 agent gateway port
  2. 调用 `l3_rpc_notifier.delete_fipnamespace_for_ext_net` 通知删除该 host 上的属于 external network 的 fip namespace 

### `def delete_csnat_router_interface_ports(self, context, router, subnet_id=None)`

1. 获取 router 上提供 snat 服务的 port
2. 调用 `core_plugin.get_ports` 获取这些 port 的数据
3. 若 subnet_ids 为空，则删除所有 port
4. 若 port 没有绑定 ip 则删除
5. 若 subnet_ids 不为空，则删除与 subnet id 一致的 port

### `def delete_floatingip_agent_gateway_port(self, context, host_id, ext_net_id)`

1. 调用 `core_plugin.get_ports` 获取属于 externel network 的 aget gateway port
2. 调用 `core_plugin.ipam.delete_port` 删除那些没有绑定 host 或者 host 与 host_id 一致的 agent gateway port

### `def _create_gw_port(self, context, router_id, router, new_network, ext_ips)`

1. 调用 `L3_NAT_dbonly_mixin._create_gw_port` 为 router 创建 gateway port
2. 若 router 为 distributed router 且存在 gateway port，则调用 `_create_snat_intf_ports_if_not_exists` 获取该 router 上提供 snat 服务的 port，若没有则创建

### `def _get_device_owner(self, context, router=None)`

返回 router 的 device_owner 属性

在 `L3_NAT_dbonly_mixin._get_device_owner` 的基础上增加了处理 distributed router 的属性

### `def _get_ports_for_allowed_address_pair_ip(self, context, network_id, fixed_ip)`

通过查询数据库 `Port` 和 `AllowedAddressPair` 获取 network_id 上 port 的 `allowed_address_pairs` 属性为 fixed_ip 的 port

### `def create_floatingip(self, context, floatingip, initial_status=const.FLOATINGIP_STATUS_ACTIVE)`

1. 调用 `L3_NAT_dbonly_mixin._create_floatingip` 创建 floating ip
2. 调用 `_notify_floating_ip_change` 发送 floating ip 更新引起的 router 更新的消息

### `def _notify_floating_ip_change(self, context, floating_ip)`

1. 获取 floating ip 绑定的 router 和 port
2. 调用 `_get_router` 获取 router 数据
3. 若 router 是 distributed router，则:
 1. 调用 `_get_dvr_service_port_hostid` 获取 port 所在的 host
 2. 调用 `_get_dvr_migrating_service_port_hostid` 获取提供 dvr 服务的 port 准备迁移到的 host 的 id
 3. 调用 `l3_rpc_notifier.routers_updated_on_host` 发送到原  host 上，router 的更新消息
 4. 若 port 确实准备迁移，则调用 `l3_rpc_notifier.routers_updated_on_host` 通知新的 host 上有 router 更新的消息
4. 若 router 不是 distributed router，则调用 `L3RpcNotifierMixin.notify_router_updated` 发送 router 更新的消息

### `def update_floatingip(self, context, id, floatingip)`

1. 调用 `_update_floatingip` 完成 floating ip 的更新
2. 调用 `_notify_floating_ip_change` 发送 floating ip 更新引起的 router 更新的 RPC 消息
3. 若 floating ip 绑定的 router 或者 port 发生了变化，也会调用 `_notify_floating_ip_change` 发送 floating ip 更新的 RPC 消息

### `def delete_floatingip(self, context, id)`

1. 调用 `_delete_floatingip` 完成 floating ip 的删除工作
2. 调用 `_notify_floating_ip_change` 发送 floating ip 删除引起的 RPC 更新的消息

### `def _update_fip_assoc(self, context, fip, floatingip_db, external_port)`

1. 调用 `L3_NAT_dbonly_mixin._update_fip_assoc` 完成 floating ip 的业务处理
2. 获取 floating ip 绑定的 router
3. 若 router 为 distributed，则调用 `_get_dvr_service_port_hostid` 检查该 port 是否用来提供 dvr 服务的，则返回该 port 的 host_id 属性
4. 若该 port 是用来提供 dvr 服务的，则调用 `create_fip_agent_gw_port_if_not_exists` 保证 agent gateway port 的存在
5. 若该 port 不是用来提供 dvr 服务的，