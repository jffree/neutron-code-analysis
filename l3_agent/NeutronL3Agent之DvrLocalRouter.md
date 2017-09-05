# Neutron L3 Agent 之 DvrLocalRouter

*neutron/agent/l3/dvr_router_base.py*

## `class DvrRouterBase(router.RouterInfo)`

实现了对 fip- namespace 相关的操作


```
    def __init__(self, agent, host, *args, **kwargs):
        super(DvrRouterBase, self).__init__(*args, **kwargs)

        self.agent = agent
        self.host = host
        self.snat_ports = None
```

### `def process(self, agent)`

```
    def process(self, agent):
        super(DvrRouterBase, self).process(agent)
        # NOTE:  Keep a copy of the interfaces around for when they are removed
        self.snat_ports = self.get_snat_interfaces()
```

新增了 `get_snat_interfaces` 的调用

### `def get_snat_interfaces(self)`

```
    def get_snat_interfaces(self):
        return self.router.get(l3_constants.SNAT_ROUTER_INTF_KEY, [])
```

### `def get_snat_port_for_internal_port(self, int_port, snat_ports=None)`

查找 int_port 中是否是一个 snat_port。

1. 若 snat_port 为空，则调用 `get_snat_interfaces` 获取当前 router 上的 snat port
2. 对比 snat_port 的 subnet 和 int_port 的 subnet，若一致，则认为该 snat_port 是为该 subnet 提供 snat 服务的 port。

## `class DvrLocalRouter(dvr_router_base.DvrRouterBase)`

```
    def __init__(self, agent, host, *args, **kwargs):
        super(DvrLocalRouter, self).__init__(agent, host, *args, **kwargs)

        self.floating_ips_dict = {}
        # Linklocal subnet for router and floating IP namespace link
        self.rtr_fip_subnet = None
        self.dist_fip_count = None
        self.fip_ns = None
        self._pending_arp_set = set()
```

### `def process(self, agent)`

1. 调用 `get_ex_gw_port` 获取 router 的 gateway port
2. 调用 `AgentMixin.get_fip_ns` 构造一个 fip- namespace
3. 调用 `RouterInfo.process` 继续处理

### `def get_floating_ips(self)`

1. 调用 `RouterInfo.get_floating_ips` 获取 router 数据中的 `_floatingips` 记录
2. 在这些 floating ip 中过滤出 host 或者 dest_host 为当前 host 的 floating ip

### `def floating_forward_rules(self, floating_ip, fixed_ip)`

重写了 `RouterInfo` 的方法

1. 调用 `fip_ns.get_rtr_ext_device_name` 获取 rfp- 设备的名称
2. 根据 rfp- 设备的名称，生成如下规则：

```
-A neutron-l3-agent-PREROUTING -d 172.16.100.245/32 -i rfp-61eaacf9-d -j DNAT --to-destination 192.168.100.5
-A neutron-l3-agent-float-snat -s 192.168.100.5/32 -j SNAT --to-source 172.16.100.245
```

### `def floating_mangle_rules(self, floating_ip, fixed_ip, internal_mark)`

1. 调用 `fip_ns.get_rtr_ext_device_name` 获取 rfp- 设备的名称
2. 为 floating ip 和 fixed ip 设定 mark

### `def floating_ip_added_dist(self, fip, fip_cidr)`

1. 调用 `_add_floating_ip_rule` 为该 floating ip 增加一个 rule 规则
2. 调用 `fip_ns.get_int_device_name` 获取 fpr- 设备名称
3. 调用 `fip_ns.get_name` 获取 fip- namespace 的名称
4. 调用 `fip_ns.local_subnets.allocate` 为当前的 router 分配一个 local subnet，该 subnet 会用到 rfp- 和 fpr- 设备上
5. 调用 `rtr_fip_subnet.get_pair` 从上面的 local subnet 中分配一对地址
6. 调用 `IPDevice` 描述 fpr- 设备
7. 为 fpr- 设备增加 route 
8. 调用 `fip_ns.get_ext_device_name` 获取 fg- 设备（agent gateway port）名称
9. 调用 `ip_lib.send_ip_addr_adv_notif` 发送 arp 通知消息，告诉大家 agent gateway port 占有该 floating ip
10. 更新 `dist_fip_count` 记录

### `def _add_floating_ip_rule(self, floating_ip, fixed_ip)`

1. 调用 `fip_ns.allocate_rule_priority` 为该 floating ip 分配一个 rule 优先级
2. 在 qrouter- namespace 中增加一条 rule 规则：

```
57483:	from 192.168.100.5 lookup 16
```

### `def _remove_floating_ip_rule(self, floating_ip)`

删除关于该 floating ip 的 rule，回收 rule priority

### `def floating_ip_removed_dist(self, fip_cidr)`

1. 调用 `fip_ns.get_rtr_ext_device_name` 获取 rfp- 设备名称
2. 调用 `fip_ns.get_int_device_name` 获取 fpr- 设备名称
3. 调用 `rtr_fip_subnet.get_pair` 获取该 router 上的 local subnet address pair
4. 调用 `fip_ns.get_name` 获取 fip- namespace name
5. 调用 `_remove_floating_ip_rule` 删除该 floating ip 的 rule
6. 调用 `IPDevice` 描述 fpr- 设备
7. 删除 floating ip 的 route 记录
8. `dist_fip_count` 减一，若 `dist_fip_count` 为0（即当前的 router 中已经没有 floating ip 的存在），则：
 1. 调用 `fip_ns.get_ext_device_name` 获取 fg- 设备的名称
 2. 调用 `IPDevice` 描述 fg- 设备，若该设备存在，则：
  1. 调用 `_get_snat_idx` 生成一个 ip route table 号
  2. 清除该 ip route table 内的 route 记录
  3. 删除该 ip route table
 3. 回收为该 route 分配的 local subnet
 4. 删除 fpr- 和 rfp- veth 设备

### `def _get_snat_idx(ip_cidr)`

根据一个 ip cidr 生产一个数字，该数字代表着该 Ip 的 route table

```
[root@node1 ~]# ip netns exec fip-6c9852c3-7a5b-4b9c-a279-b9098257a0dd ip rule
0:	from all lookup local 
32766:	from all lookup main 
32767:	from all lookup default 
2852022899:	from all iif fpr-61eaacf9-d lookup 2852022899
```

这里面的  2852022899 就是这个方法生成的

### `def floating_ip_moved_dist(self, fip)`

一个 floating ip 绑定的 fixed ip 发生了变化

1. 调用 `_remove_floating_ip_rule` 清除该 floating ip 之前的 rule
2. 调用 `_add_floating_ip_rule` 为该 floating ip 重新分配 rule

### `def add_floating_ip(self, fip, interface_name, device)`

实现 RouterInfo 中的方法

1. 调用 `floating_ip_added_dist` 为该 floating ip 建立相应的规则和辅助设备
2. 返回 active 状态

### `def remove_floating_ip(self, device, ip_cidr)`

实现 RouterInfo 中的方法

* 调用 `floating_ip_removed_dist` 方法实现

### `def move_floating_ip(self, fip)`

调用 `floating_ip_moved_dist` 方法实现

### `def _get_internal_port(self, subnet_id)`

获取当前 router 上属于 subnet 的 internal port

### `def _update_arp_entry(self, ip, mac, subnet_id, operation)`

1. 调用 `_get_internal_port` 获取当前 router 上属于 subnet 的 internal port
2. 调用 `get_internal_device_name` 获取该 port 的名称
3. 调用 `IPDevice` 描述该 port
4. 若该 port 真实存在，则根据 operation 来增加或删除 arp 记录
5. 若 port 不存在，且 operation 为 add，则调用 `_cache_arp_entry` 来缓存来 arp 记录，等到 port 存在后再增加记录

### `def _cache_arp_entry(self, ip, mac, subnet_id, operation)`

缓存 arp 记录

1. 以一个 `Arp_entry` 来描述该 arp 记录，及其操作类型
2. 将该记录保存在 `_pending_arp_set` 中

### `def _process_arp_cache_for_internal_port(self, subnet_id)`

处理与 subnet 有关的 arp 缓存记录，调用 `_update_arp_entry` 实现

### `def _delete_arp_cache_for_internal_port(self, subnet_id)`

删除与 subnet 有关的 arp 缓存记录

### `def _set_subnet_arp_info(self, subnet_id)`

1. 调用 `AgentMixin.get_ports_by_subnet` 获取该 subnet 上的 port
2. 调用 `_update_arp_entry` 更新关于这些 port 的 arp 记录
3. 调用 `_process_arp_cache_for_internal_port` 出该关于该 subnet 的 arp 缓存记录

```
[root@node1 ~]# ip netns exec qrouter-61eaacf9-d4e0-4202-bac9-321da0ceaa69 arp -n
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.100.2            ether   fa:16:3e:a3:93:e9   CM                    qr-d555da2e-f3
10.10.10.8               ether   fa:16:3e:63:d7:ff   CM                    qr-f5b8c40f-24
10.10.10.2               ether   fa:16:3e:81:36:c2   CM                    qr-f5b8c40f-24
192.168.100.12           ether   fa:16:3e:44:db:f0   CM                    qr-d555da2e-f3
169.254.106.115          ether   de:50:a0:c4:aa:21   C                     rfp-61eaacf9-d
192.168.100.10           ether   fa:16:3e:1c:50:80   CM                    qr-d555da2e-f3
10.10.10.13              ether   fa:16:3e:68:e7:3e   CM                    qr-f5b8c40f-24
192.168.100.5            ether   fa:16:3e:41:24:fc   CM                    qr-d555da2e-f3
```

### `def _delete_gateway_device_if_exists(self, ns_ip_device, gw_ip_addr, snat_idx)`

删除关于 ip route 表 snat_idx 中的默认网关记录

### `def _stale_ip_rule_cleanup(self, ns_ipr, ns_ipd, ip_version)`

清除某一 namespace 中，ip rule priority 大于 72768 的 rule 以及相关的 ip route table 数据

### `def gateway_redirect_cleanup(self, rtr_interface)`

调用 `_stale_ip_rule_cleanup` 清除 qrouter- namespace 中关于 rfp- 设备的 route 记录

### `def _snat_redirect_add(self, gateway, sn_port, sn_int)`

```
    def _snat_redirect_add(self, gateway, sn_port, sn_int):
        """Adds rules and routes for SNAT redirection."""
        self._snat_redirect_modify(gateway, sn_port, sn_int, is_add=True)
```

### `def _snat_redirect_remove(self, gateway, sn_port, sn_int)`

```
    def _snat_redirect_remove(self, gateway, sn_port, sn_int):
        """Removes rules and routes for SNAT redirection."""
        self._snat_redirect_modify(gateway, sn_port, sn_int, is_add=False)
```

### `def _snat_redirect_add_from_port(self, port)`

1. 调用 `get_ex_gw_port` 获取 gateway port，若不存在 gateway port 则退出
2. 调用 `get_snat_port_for_internal_port` 获取为该 subnet 提供 snat 服务的 snat_port
3. 调用 `get_internal_device_name` 获取 port 的名称
4. 调用 `_snat_redirect_add`

### `def _snat_redirect_modify(self, gateway, sn_port, sn_int, is_add)`

1. 构造 `IPRule` 来描述 qrouter- namespace 的 rule
2. 构造 `IPDevice` 来描述 interface
3. 若是添加 rule 和 route，则构造一个 `IPWrapper` 实例
4. 对于 sn_port 上的每个 fixed ip：
 * 对于提供 snat 服务的端口 gateway，若其上面的 ip 地址与 sn_port 上面的地址一致的话
  1. 若是增加 rule 和 route，则为 sn_int 增加新的 rule 和 route table，同时使用如下命令：`sysctl -w net.ipv4.conf.%s.send_redirects=0`
  2. 若是删除操作的话，则调用 `_delete_gateway_device_if_exists` 删除网关和路由记录，删除 rule 记录

* 举例子来说就是将对外部网络的请求转发到 snat- namespace 中的网卡上

```
[root@node1 ~]# ip netns exec qrouter-61eaacf9-d4e0-4202-bac9-321da0ceaa69 ip rule
0:	from all lookup local 
32766:	from all lookup main 
32767:	from all lookup default 
57483:	from 192.168.100.5 lookup 16 
168430081:	from 10.10.10.1/24 lookup 168430081 
3232261121:	from 192.168.100.1/24 lookup 3232261121
```

```
[root@node1 ~]# ip netns exec qrouter-61eaacf9-d4e0-4202-bac9-321da0ceaa69 ip route list table 168430081
default via 10.10.10.13 dev qr-f5b8c40f-24
```

```
[root@node1 ~]# ip netns exec snat-61eaacf9-d4e0-4202-bac9-321da0ceaa69 ip addr show sg-1d0b51ca-38
83: sg-1d0b51ca-38: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UNKNOWN qlen 1000
    link/ether fa:16:3e:68:e7:3e brd ff:ff:ff:ff:ff:ff
    inet 10.10.10.13/24 brd 10.10.10.255 scope global sg-1d0b51ca-38
       valid_lft forever preferred_lft forever
    inet6 fe80::f816:3eff:fe68:e73e/64 scope link 
       valid_lft forever preferred_lft forever
```

### `def internal_network_added(self, port)`

1. 调用 `RouterInfo.internal_network_added` 创建新的 router port 
2. 调用 `_set_subnet_arp_info` 更新该 port 所在 subnet 的 arp 记录
3. 调用 `_snat_redirect_add_from_port` 为该 port 实现 snat 的规则

### `def internal_network_removed(self, port):`

1. 调用 `_dvr_internal_network_removed` 处理 snat 和 arp 的事项
2. 调用 `RouterInfo.internal_network_removed` 删除该 port

### `def _dvr_internal_network_removed(self, port)`

1. 若不存在 gateway port 则直接退出
2. 调用 `get_snat_port_for_internal_port` 获取提供 snat 服务的 port，若不存在则直接退出
3. 调用 `_snat_redirect_remove` 删除与该 port 有关的 snat 规则
4. 调用 `_delete_arp_cache_for_internal_port` 删除与该 port 有关的 arp 缓存

### `def get_floating_agent_gw_interface(self, ext_net_id)`

获取 external netwokr 在该 router 上的 agent gateway

### `def get_external_device_interface_name(self, ex_gw_port)`

获取 rfp- 设备的名称

### `def external_gateway_added(self, ex_gw_port, interface_name)`

1. 在 qrouter- namespace 中执行如下命令 `sysctl -w net.ipv4.conf.all.send_redirects=0`
2. 对于所有的 internal port：
 1. 调用 `get_snat_port_for_internal_port` 获取与之对应的 snat port
 2. 调用 `get_internal_device_name` 获取 internal port 的名称
 3. 调用 `_snat_redirect_add` 实现 snat 功能
3. 对于所有的 snat port，调用 `_update_arp_entry` 更新 qrouter- namespace 的 arp 记录

### `def external_gateway_updated(self, ex_gw_port, interface_name)`

未实现

### `def external_gateway_removed(self, ex_gw_port, interface_name)`

1. 调用 `process_floating_ip_nat_rules` 重新处理与 floating ip 有关的 iptables rule
2. 若存在 fip- namespace，调用 `get_external_device_interface_name` 获取 rfp- 网络设备名称，调用 `process_floating_ip_addresses`
3. 若 router 不存在 gateway port，则对于所有的 internal port 来说：
 1. 调用 `get_snat_port_for_internal_port` 获取 snat port
 2. 调用 `get_internal_device_name` 获取 internal port name
 3. 调用 `_snat_redirect_remove` 删除 snat 的相应规则

### `def _handle_router_snat_rules(self, ex_gw_port, interface_name)`

1. 清空 ipv4 中的 snat 和 POSTROUTING chain
2. 获取 gateway port，没有则直接退出
3. 调用 `get_external_device_interface_name` 获取 rfp- 的名称
4. 调用 `get_floating_ips` 获取所有的 floating ip
5. 将 snat chain 转发至 floating-snat chain
6. 调用 `_prevent_snat_for_internal_traffic_rule` 增加如下规则：`-A neutron-l3-agent-POSTROUTING ! -i rfp-61eaacf9-d ! -o rfp-61eaacf9-d -m conntrack ! --ctstate DNAT -j ACCEPT`

### `def _get_address_scope_mark(self)`

1. 获取 internal port
2. 调用 `_get_port_devicename_scopemark` 获取 internal port 对于的 mark/mask
3. 调用 `get_ex_gw_port` 获取 gateway port
4. 调用 `get_external_device_interface_name` 获取 rfp- 设备名称
5. 调用 `_get_external_address_scope` 获取 external network 的 scope address
6. 调用 `get_address_scope_mark_mask` 获取 external network 的 mark/mask
7. 返回所有 port 的 mark/mask

### `def process_external(self, agent)`

1. 若存在 gateway port，则调用 `create_dvr_fip_interfaces` 处理 agent gateway port 相关事项
2. 调用 `RouterInfor.process_external` 继续处理

### `def create_dvr_fip_interfaces(self, ex_gw_port)`

1. 调用 `get_floating_ips` 获取所有的 floating ip
2. 调用 `get_floating_agent_gw_interface` 获取 agent gateway port name
3. 若存在 floating ip：
 1. 若不存在 agent gateway port，调用 `plugin_rpc.get_agent_gateway_port` 获取其数据
 2. 调用 `fip_ns.create_or_update_gateway_port` 创建 agent gateway port
 3. 创建 fpr- 和 rfp- 设备，并更新路由信息

### `def update_routing_table(self, operation, route)`

1. 若存在 fip- namespace 和 agent gateway port，则：
 1. 获取 fip- namespace 的名称
 2. 获取 agent gateway port 数据
 3. 调用 `_check_if_route_applicable_to_fip_namespace` 是否可以为 router 在 agnet gateway 上创建 route
 4. 若可以创建 route，则：
  1. 获取 local subnet pair
  2. 调用 `_get_snat_idx` 获取 snat table number
  3. 调用 `_update_fip_route_table_with_next_hop_routes` 为 fpr- 创建通往外部的路由
2. 继续调用 `RouterInfo.update_routing_table` 处理其他事项

### `def _check_if_route_applicable_to_fip_namespace(self, route, agent_gateway_port)`

1. 获取 agent gateway port 的 ip 地址
2. 若 `router['nexthop']` 属性与 agent gateway port 所在的 subnet 为同一个，则返回 True

### `def _update_fip_route_table_with_next_hop_routes(self, operation, route, fip_ns_name, tbl_index)`
 
```
    def _update_fip_route_table_with_next_hop_routes(
        self, operation, route, fip_ns_name, tbl_index):
        cmd = ['ip', 'route', operation, 'to', route['destination'],
               'via', route['nexthop'], 'table', tbl_index]
        ip_wrapper = ip_lib.IPWrapper(namespace=fip_ns_name)
        if ip_wrapper.netns.exists(fip_ns_name):
            ip_wrapper.netns.execute(cmd, check_exit_code=False)
        else:
            LOG.debug("The FIP namespace %(ns)s does not exist for "
                      "router %(id)s",
                      {'ns': fip_ns_name, 'id': self.router_id})
```

```
[root@node2 ~]# ip netns exec fip-6c9852c3-7a5b-4b9c-a279-b9098257a0dd ip -d route show table 2852019551
default via 172.16.100.1 dev fg-eff4564f-5f
```

### `def get_router_cidrs(self, device)`

1. 若不存在 fip- namespace 则返回空
2. 调用 `fip_ns.get_int_device_name` 获取 fpr- 设备名称
3. 调用 `IPDevice` 封装 fpr- 涉笔
4. 若 fpr- 设备不存在，则返回空
5. 获取经过 fpr- 设备的路由记录（`172.16.100.246 via 169.254.93.94 dev fpr-61eaacf9-d `）
6. 获取路由中的 floating ip