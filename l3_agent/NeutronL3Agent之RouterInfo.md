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

1. 调用 `create_router_namespace_object` 创建一个 `RouterNamespace` 对象（用来管理 qrouter- namespace）
2. 创建一个 `IptablesManager` 对象，用于对 qrouter- 下的 Iptables 进行操作
3. 调用 `initialize_address_scope_iptables`


### `def create_router_namespace_object(self, router_id, agent_conf, iface_driver, use_ipv6):`

```
    def create_router_namespace_object(
            self, router_id, agent_conf, iface_driver, use_ipv6):
        return namespaces.RouterNamespace(
            router_id, agent_conf, iface_driver, use_ipv6)
```

### `def initialize_address_scope_iptables(self)`

```
    def initialize_address_scope_iptables(self):
        self._initialize_address_scope_iptables(self.iptables_manager)
```

### `def _initialize_address_scope_iptables(self, iptables_manager)`

* 在 qrouter- namespace 上，做一下 iptables 的操作（我们这里只拿 ipv4 解释）：
 1. 对于 mangle 表：
```
-N neutron-l3-agent-float-snat
-N neutron-l3-agent-floatingip
-N neutron-l3-agent-scope
-A neutron-l3-agent-PREROUTING -j neutron-l3-agent-scope
-A neutron-l3-agent-PREROUTING -m connmark ! --mark 0x0/0xffff0000 -j CONNMARK --restore-mark --nfmask 0xffff0000 --ctmask 0xffff0000
-A neutron-l3-agent-PREROUTING -j neutron-l3-agent-floatingip
-A neutron-l3-agent-float-snat -m connmark --mark 0x0/0xffff0000 -j CONNMARK --save-mark --nfmask 0xffff0000 --ctmask 0xffff0000
```
 2. 对于 filter 表：
```
-N neutron-l3-agent-scope
-A neutron-l3-agent-FORWARD -j neutron-l3-agent-scope
```

* 注释：
 1. 数据包标记(nfmark)
 2. 连接标记(ctmark)

* 参考

[iptables详解（一）](http://www.51niux.com/?id=100)

### `def initialize(self, process_monitor)`

1. 创建一个 `DaemonMonitor` 实例，用来管理 `radvd` 服务
2. 创建 qrouter- namespace

### `def router(self)`

```
    @property
    def router(self):
        return self._router

    @router.setter
    def router(self, value):
        self._router = value
        if not self._router:
            return
        # enable_snat by default if it wasn't specified by plugin
        self._snat_enabled = self._router.get('enable_snat', True)
```

属性方法，router 数据的读取和设置。
设置 router 数据时，判断该 router 是否支持 snat

### `def get_internal_device_name(self, port_id)`

获取 qr- 网络设备的名称

### `def get_external_device_name(self, port_id)`

获取 qg- 网络设备的名称

### `def get_external_device_interface_name(self, ex_gw_port)`

```
    def get_external_device_interface_name(self, ex_gw_port):
        return self.get_external_device_name(ex_gw_port['id'])
```

### `def update_routing_table(self, operation, route)`

```
    def update_routing_table(self, operation, route):
        self._update_routing_table(operation, route, self.ns_name)
```

### `def _update_routing_table(self, operation, route, namespace)`

在当前的 qrouter- namespace 下，调用 ip route 命令更新路由表

### `def routes_updated(self, old_routes, new_routes)`

1. 调用 `common_utils.diff_list_of_dict` 找出增加和删除的 route
2. 调用 `update_routing_table` 实现 route 记录的删除和替换

### `def get_ex_gw_port(self)`

```
    def get_ex_gw_port(self):
        return self.router.get('gw_port')
```

### `def get_floating_ips(self)`

```
    def get_floating_ips(self):
        """Filter Floating IPs to be hosted on this agent."""
        return self.router.get(lib_constants.FLOATINGIP_KEY, [])
```

### `def floating_forward_rules(self, floating_ip, fixed_ip)`

根据 floating ip 和 fixed ip 的匹配，构造 snat 和 dnat 的功能。

在 qrouter- namespace 中：

```
-A neutron-l3-agent-PREROUTING -d 172.16.100.245/32 -i rfp-61eaacf9-d -j DNAT --to-destination 192.168.100.5
-A neutron-l3-agent-float-snat -s 192.168.100.5/32 -j SNAT --to-source 172.16.100.245
```

```
    def floating_forward_rules(self, floating_ip, fixed_ip):
        return [('PREROUTING', '-d %s/32 -j DNAT --to-destination %s' %
                 (floating_ip, fixed_ip)),
                ('OUTPUT', '-d %s/32 -j DNAT --to-destination %s' %
                 (floating_ip, fixed_ip)),
                ('float-snat', '-s %s/32 -j SNAT --to-source %s' %
                 (fixed_ip, floating_ip))]
```

* 貌似 OUTPUT chain 中的这个未实现

### `def floating_mangle_rules(self, floating_ip, fixed_ip, internal_mark)`

```
    def floating_mangle_rules(self, floating_ip, fixed_ip, internal_mark):
        mark_traffic_to_floating_ip = (
            'floatingip', '-d %s/32 -j MARK --set-xmark %s' % (
                floating_ip, internal_mark))
        mark_traffic_from_fixed_ip = (
            'FORWARD', '-s %s/32 -j $float-snat' % fixed_ip)
        return [mark_traffic_to_floating_ip, mark_traffic_from_fixed_ip]
```

为 floating ip 设定 mangle 表的规则

*这个貌似也没有实现*

### `def get_address_scope_mark_mask(self, address_scope=None)`

生成 mark 标记，默认都是：`0x4000000/0xffff0000`

### `def get_port_address_scope_mark(self, port)`

调用 `get_address_scope_mark_mask` 为 port 上的所有 address_scope 生成 mark

### `def process_floating_ip_nat_rules(self)`

1. 先清除 nat 表中带有 `floating_ip` tag 的 rule
2. 调用 `get_floating_ips` 获取该 router 上的 floating ip
3. 调用 `floating_forward_rules` 构造关于 floating ip 的 rule
4. 应用这些 iptables rule

### `def process_floating_ip_address_scope_rules(self)`

* 情况说明：

可能有些与 floating ip 绑定的 fixed ip 的 address scope 与 gateway port 的 fixed ip 所在的 address scope 不一致，该方法就是来为这些 floating ip 和 fixed ip 增加 iptables rule 的

1. 先清除 mangle 表上的 floating_ip 有关的 rule
2. 调用 `get_floating_ips` 获取所有的 floating ip
3. 调用 `_get_external_address_scope` 获取 external gateway port 上 ipv4 的 address scope
4. 过滤掉 floating ip 的 fixed ip address scope 与 external gateway port 一致的 floating ip
5. 若存在不与 gateway port 绑定的 floating ip，则：
 1. 调用 `get_address_scope_mark_mask` 为 external gateway port 上的 ipv4 地址创建 mark/mask
 2. 调用 `_get_address_scope_mark` 获取该 router 上所有 port 的 address scope 的 mark/mask
 3. 为该 port 设置 mark
6. 对于所有的不与 gateway port 绑定的 floating ip：
 1. 获取与这些 floating ip 绑定的 internal fixed ip
 2. 获取 fixed ip 的 address scope
 3. 调用 `floating_mangle_rules` 生成 fixed ip 与 floating ip 的 mangle mark 规则
 4. 应用这些规则

### `def _get_external_address_scope(self)`

获取 external gateway port 上 ipv4 的 address scope

### `def _get_address_scope_mark(self)`

1. 获取 router 上的 interface（这里不包含 gatway port，我们将这些 port 称为  Internal port）
2. 调用 `_get_port_devicename_scopemark` 获取这些 interface 的 address scope mark/mask
3. 调用 `get_ex_gw_port` 获取 router 的 gateway port
4. 若存在 gateway port，则调用 `_get_port_devicename_scopemark` 为 gateway port address scope 创建 mark/mask，并将其与 Internal port 的数据合并在一起
5. 返回该 router 上所有 port 的 address scope 的 mark/mask

### `def _get_port_devicename_scopemark(self, ports, name_generator)`

* 对于所有的 ports：
 1. 获取该 port 在 host 上的 name
 2. 获取 port 的 ip 地址的 cidr
 3. 调用 `get_port_address_scope_mark` 获取该 port 的 address_scope 的 mark/mask
 4. 构造该 port 的 address_scope 的 mark/mask 信息

### `def process_snat_dnat_for_fip(self)`

```
    def process_snat_dnat_for_fip(self):
        try:
            self.process_floating_ip_nat_rules()
        except Exception:
            # TODO(salv-orlando): Less broad catching
            msg = _('L3 agent failure to setup NAT for floating IPs')
            LOG.exception(msg)
            raise n_exc.FloatingIpSetupException(msg)
```

调用 `process_floating_ip_nat_rules` 实现 snat 表中，floating ip 与 fixed ip 的 snat 与 dnat 的转换

### `def _add_fip_addr_to_device(self, fip, device)`

为某个网络设备增加一个 floating ip 地址

### `def add_floating_ip(self, fip, interface_name, device)`

待实现

### `def gateway_redirect_cleanup(self, rtr_interface)`

未实现

### `def remove_floating_ip(self, device, ip_cidr)`

```
    def remove_floating_ip(self, device, ip_cidr):
        device.delete_addr_and_conntrack_state(ip_cidr)
```

从某个网络设备上删除 floating ip 的地址，并调用 `conntrack` 清除与该 floating ip 有关的连接记录

### `def move_floating_ip(self, fip)`

```
    def move_floating_ip(self, fip):
        return lib_constants.FLOATINGIP_STATUS_ACTIVE
```

### `def remove_external_gateway_ip(self, device, ip_cidr)`

删除设备的上的 ip_cidr 地址，清除其连接记录

### `def get_router_cidrs(self, device)`

获取网络设备的 ip cidr

### ` def process_floating_ip_addresses(self, interface_name)`

1. 以 `IPDevice` 来描述该设备
2. 调用 `get_router_cidrs` 获取该设备上已经存在的 Ip 地址
3. 调用 `_get_gw_ips_cidr` 获取网关上的 ipv4 版本的地址
4. 调用 `get_floating_ips` 获取该 router 上的 floating ip
5. 对于所有的 floating ip：
 1. 若当前的设备上没有，则给其添加上
 2. 若 floating ip 绑定的 fixed ip 发生了变化，则调用 `move_floating_ip` 返回其 active 状态
 3. 若 floating ip 的状态无变化，则将其置为 `NOCHANGE`
6. 获取该设备上那些被删除掉的 floating ip
7. 调用 `remove_floating_ip` 从该设备上删除那些被删除掉的 floating ip

### `def _get_gw_ips_cidr(self)`

1. 调用 `get_ex_gw_port` 获取网关地址
2. 获取该网关上的 ipv4 地址

### `def configure_fip_addresses(self, interface_name)`

调用 `process_floating_ip_addresses` 实现

### `def put_fips_in_error_state(self)`

```
    def put_fips_in_error_state(self):
        fip_statuses = {}
        for fip in self.router.get(lib_constants.FLOATINGIP_KEY, []):
            fip_statuses[fip['id']] = lib_constants.FLOATINGIP_STATUS_ERROR
        return fip_statuses
```

将 router 上的所有 floating ip 都置为 error 状态

### `def delete(self, agent)`

1. 清空该 router 的 gw_port、interface、floating ip 记录
2. 调用 `process_delete` 删除 internal 和 external port
3. 调用 `disable_radvd` 停止 radvr 服务
4. 删除 qrouter- namespace

### `def disable_radvd(self)`

```
    def disable_radvd(self):
        LOG.debug('Terminating radvd daemon in router device: %s',
                  self.router_id)
        self.radvd.disable()
```

### `def process_delete(self, agent)`

1. 若当前还存在 qrouter- namespace，则：
 1. 调用 `_process_internal_ports` 处理 internal port 的删除问题
 2. 调用 `_process_external_on_delete` 删除 external port

### `def _process_internal_ports(self, pd)`

1. 获取当前记录的 Interface
2. 根据记录获取新的 port 和 旧  port
3. 调用 `_get_updated_ports` 获取 ip 地址发生变化的 port（更新的 port。**所以：**这里一共有三种 port，一种是新增加的、一种是不再需要的旧的、一种是发生了更新的）
4. 对于新增的 port，调用 `internal_network_added` 增加新的 port
5. 对于不再需要的 port，调用 `internal_network_removed` 删除 port
6. 对于更新的 port，调用 `internal_network_updated` 重新设置 port 的 ip
7. 处理当前 router 上 port 的 ipv6 事项
8. 启动 radvd 服务
9. 再次判断是否还存在不应该存在的 port，对其进行删除

### `def _get_updated_ports(existing_ports, current_ports)`

获取已经存在的但 ip 地址发生变化的 port

### `def internal_network_added(self, port)`

调用 `_internal_network_added` 实现

### `def _internal_network_added(self, ns_name, network_id, port_id, fixed_ips, mac_address, interface_name, prefix, mtu=None)`

1. 调用 interface driver plug 增加 port
2. 调用 interface driver init_router_port 为 port 添加 ip，并初始化 port 的 route
3. 调用 `ip_lib.send_ip_addr_adv_notif` 发送 arp 通知

### `def internal_network_removed(self, port)`

1. 调用 `ip_lib.device_exists` 判断该设备是否存在
2. 调用 interface driver unplug 删除该 port

### `def internal_network_updated(self, interface_name, ip_cidrs)`

```
    def internal_network_updated(self, interface_name, ip_cidrs):
        self.driver.init_router_port(
            interface_name,
            ip_cidrs=ip_cidrs,
            namespace=self.ns_name)
```

设置 port 的 ip，更新其 route 记录

### `def _process_external_on_delete(self, agent)`

1. 调用 `get_ex_gw_port` 获取 gateway port
2. 调用 `_process_external_gateway` 清理所有的 gateway port
3. 调用 `get_external_device_interface_name` 获取 gateway port 的名称
4. 调用 `configure_fip_addresses` 处理 gatway port floating ip

### `def _process_external_gateway(self, ex_gw_port, pd)`

1. 调用 `get_external_device_name` 获取 gateway port 的名称
2. 若是当前 router 数据中还不存在 external gateway port 则调用 `external_gateway_added` 为 router 增加 gateway
3. 若 router 中已经存在 external gateway port 的记录，则调用 `_gateway_ports_equal` 判断数据是否相等，若是不相等，则调用 `external_gateway_updated` 更新 gateway port
4. 若 router 中存在 gateway port 的记录，但是 ex_gw_port 不存在，则调用 `external_gateway_removed` 清除 gateway port
5. 若二者同时不存在，则调用 `gateway_redirect_cleanup`
6. 调用 `_delete_stale_external_devices` 删除那些与 gateway port name 不一致的 qg- 设备
7. 调用 `_handle_router_snat_rules` 情况 snat 规则

### `def external_gateway_added(self, ex_gw_port, interface_name)`

```
    def external_gateway_added(self, ex_gw_port, interface_name):
        preserve_ips = self._list_floating_ip_cidrs()
        self._external_gateway_added(
            ex_gw_port, interface_name, self.ns_name, preserve_ips)
```

### `def _external_gateway_added(self, ex_gw_port, interface_name, ns_name, preserve_ips)`

1. 调用 `_plug_external_gateway` 增加 gateway port
2. 调用 `_get_external_gw_ips` 获取 gateway port 所在 subnet 的 gateway ip
3. 调用 `_add_route_to_gw` 增加 gateway route 记录
4. 调用 interface driver init_router_port 方法为该 port 增加 ip 和对于的 route
5. 获取 gateway port 初始化完成后与其绑定的 gateway ip
6. 对于那些没有使用的 gateway ip，删除其路由记录
7. 对于那些正在使用的 gateway ip，增加其路由记录
8. 调用 `ip_lib.send_ip_addr_adv_notif` 发送 arp 通知

### `def _plug_external_gateway(self, ex_gw_port, interface_name, ns_name)`

调用 interface driver plug 创建 gateway port

### `def _get_external_gw_ips(self, ex_gw_port)`

获取 gateway port 所在 subnet 的 gateway ip

### `def _add_route_to_gw(self, ex_gw_port, device_name, namespace, preserve_ips)`

* 对于 gateway 上的所有 subnet：
 1. 判断 subnet 的 gateway ip 是否在 subnet 内
 2. 若不在 subnet 内，则调用 `IPDevice.route.add_route` 增加此 ip route

### `def _gateway_ports_equal(port1, port2)`

```
    @staticmethod
    def _gateway_ports_equal(port1, port2):
        return port1 == port2
```

### `def external_gateway_updated(self, ex_gw_port, interface_name)`

```
    def external_gateway_updated(self, ex_gw_port, interface_name):
        preserve_ips = self._list_floating_ip_cidrs()
        self._external_gateway_added(
            ex_gw_port, interface_name, self.ns_name, preserve_ips)
```

### `def external_gateway_removed(self, ex_gw_port, interface_name)`

1. 调用 `IPDevice` 来描述该设备
2. 调用 `remove_external_gateway_ip` 删除 gateway port 的 Ip 地址
3. 调用 interface driver unplug 删除该设备

### `def _delete_stale_external_devices(self, interface_name, pd)`

删除名称与 interface_name 不一样的 external port 

### `def _handle_router_snat_rules(self, ex_gw_port, interface_name)`

1. 调用 `_empty_snat_chains` 清空与 snat 有关的 chain
2. 将 snat 转发至 floating-nat chain
3. 调用 `_add_snat_rules` 处理相应的规则

### `def _empty_snat_chains(self, iptables_manager)`

清空该 qrouter- 上的 nat 表与 mangle 表上的 POSTROUTING、snat、mark chain

### `def _add_snat_rules(self, ex_gw_port, iptables_manager, interface_name)`

1. 调用 `process_external_port_address_scope_routing` 处理 gateway port address scope 的 route
2. 若存在 gateway port，则：
 * 若该 gateway port 上绑定有 ipv4 地址：
  1. 调用 `external_gateway_nat_snat_rules` 增加 snat 规则
  2. 调用 `external_gateway_nat_fip_rules` 增加
  3. 调用 `external_gateway_mangle_rules` 生成 mangle 表的规则

### `process_external_port_address_scope_routing`

1. 若不支持 snat 则退出
2. 若不存在 gateway port 则退出
3. `-A neutron-l3-agent-POSTROUTING -o qg-c68ba5c4-7b -m connmark --mark 0x0/0xffff0000 -j CONNMARK --save-mark --nfmask 0xffff0000 --ctmask 0xffff0000`
4. 调用 `_get_external_address_scope` 获取 external network address scope，为其增加相应的规则

### ` def external_gateway_nat_snat_rules(self, ex_gw_ip, interface_name)`

对 gateway port 增加 snat 规则

### `def external_gateway_nat_fip_rules(self, ex_gw_ip, interface_name)`

1. 调用 `_prevent_snat_for_internal_traffic_rule` 阻止内部网络之间走 snat 方法
2. 增加如下规则：

```
-A neutron-l3-agent-snat -m mark ! --mark 0x2/0xffff -m conntrack --ctstate DNAT -j SNAT --to-source 172.16.100.247
```

### `def _prevent_snat_for_internal_traffic_rule(self, interface_name)`

nat 表增加如下规则：

```
-A neutron-l3-agent-POSTROUTING ! -i qg-c68ba5c4-7b ! -o qg-c68ba5c4-7b -m conntrack ! --ctstate DNAT -j ACCEPT
```

### `def external_gateway_mangle_rules(self, interface_name)`

```
-A neutron-l3-agent-scope -i qg-c68ba5c4-7b -j MARK --set-xmark 0x4000000/0xffff0000
```

### `def configure_fip_addresses(self, interface_name)`

调用 `process_floating_ip_addresses` 实现

### `def _internal_network_updated(self, port, subnet_id, prefix, old_prefix, updated_cidrs)`

与 ipv6 相关

### `def _get_existing_devices(self)`

获取当前的 namespace 中存在的网络设备

### `def _port_has_ipv6_subnet(port)`

判断 port 上是否含有 ipv6 地址 subnet

### `def address_scope_mangle_rule(self, device_name, mark_mask)`

```
    def address_scope_mangle_rule(self, device_name, mark_mask):
        return '-i %s -j MARK --set-xmark %s' % (device_name, mark_mask)
```

### `def address_scope_filter_rule(self, device_name, mark_mask)`

```
    def address_scope_filter_rule(self, device_name, mark_mask):
        return '-o %s -m mark ! --mark %s -j DROP' % (
            device_name, mark_mask)
```

### `def _enable_ra_on_gw(self, ex_gw_port, ns_name, interface_name)`

在 Interface 上启动 ipv6 ra

### `def is_v6_gateway_set(self, gateway_ips)`

判断 ip 中是否含有 ipv6 版本的地址

### `def update_fip_statuses(self, agent, fip_statuses)`

调用 `plugin_rpc.update_floatingip_statuses` 更新 Server 端 floating ip 的状态

### `def _add_address_scope_mark(self, iptables_manager, ports_scopemark)`

1. 调用 `address_scope_mangle_rule`
2. 调用 `address_scope_filter_rule`

### `def process_ports_address_scope_iptables(self)`

```
    def process_ports_address_scope_iptables(self):
        ports_scopemark = self._get_address_scope_mark()
        self._add_address_scope_mark(self.iptables_manager, ports_scopemark)
```

### `def process_address_scope(self)`

```
    def process_address_scope(self):
        with self.iptables_manager.defer_apply():
            self.process_ports_address_scope_iptables()
            self.process_floating_ip_address_scope_rules()
```

### `def process(self, agent)`

1. 调用 `_process_internal_ports` 更新 l3 agent 上的 internal port
2. 调用 `process_external` 更新 l3 agent 上的 external port
3. 调用 `process_address_scope` 处理 address scope 相关
4. 调用 `routes_updated` 更新 route 
5. 更新自身的 ex_gw_port、fip_map、enable_snat 数据