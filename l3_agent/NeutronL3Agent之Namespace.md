# Neutron L3 Agent Namespace

与 l3 agent 有关的 namespace 有三种：qrouter-、sant-、fip-


## `class Namespace(object)`

*neutron/agent/l3/namespace.py*

namespace 的基类

```
    def __init__(self, name, agent_conf, driver, use_ipv6):
        self.name = name
        self.ip_wrapper_root = ip_lib.IPWrapper()
        self.agent_conf = agent_conf
        self.driver = driver
        self.use_ipv6 = use_ipv6
```

### `def create(self)`

1. 调用 `IPWrapper.ensure_namespace` 创建 namespace 
2. 执行 `sysctl -w net.ipv4.ip_forward=1`
3. 若使用 ipv6，则执行 `sysctl -w net.ipv6.conf.all.forwarding=1`

### `def delete(self)`

调用  `IPWrapper` 删除掉 namespace 

### `def exists(self)`

调用 `IPWrapper` 检查该 namespace 是否存在

## `class RouterNamespace(Namespace)`

qrouter- 类型的 namespace

```
    def __init__(self, router_id, agent_conf, driver, use_ipv6):
        self.router_id = router_id
        name = self._get_ns_name(router_id)
        super(RouterNamespace, self).__init__(
            name, agent_conf, driver, use_ipv6)
```

### `def _get_ns_name(cls, router_id)`

```
    @classmethod
    def _get_ns_name(cls, router_id):
        return build_ns_name(NS_PREFIX, router_id)
```

调用 `buil_ns_name` 创建一个 namespace name

### `def delete(self)`

1. 调用 `IPWrapper.get_devices` 获取当前 namespace 下的所有网络设备（lo 除外）
2. 删除 namespace 下的网络设备：
 1. 调用 interface driver 删除 `qr-` 设备
 2. 调用 `IPWrapper.del_veth` 删除 `rfp-` veth 设备
 3. 调用 interface dirver 删除 `qg-` 设备
3. 调用 `Namespace.delete` 删除该 namespace

## `class SnatNamespace(namespaces.Namespace)`

```
    def __init__(self, router_id, agent_conf, driver, use_ipv6):
        self.router_id = router_id
        name = self.get_snat_ns_name(router_id)
        super(SnatNamespace, self).__init__(
            name, agent_conf, driver, use_ipv6)
```

### `def get_snat_ns_name(cls, router_id)`

```
    @classmethod
    def get_snat_ns_name(cls, router_id):
        return namespaces.build_ns_name(SNAT_NS_PREFIX, router_id)
```

获取 namespace 的名称

### `def create(self)`

1. 调用 `Namespace.create` 完成 namespace 的创建
2. 在该 namespace 下执行如下命令：`sysctl -w net.ipv4.ip_nonlocal_bind=0`

```
/proc/sys/net/ipv4/ip_nonlocal_bind
如果你希望你的应用程序能够绑定到不属于本地网卡的地址上时，设置这个选项。如果你的机器没有专线连接(甚至是动态连接)时非常有用，即使你的连接断开，你的服务也可以启动并绑定在一个指定的地址上。
```

### `def delete(self)`

1. 调用 `IPWrapper.get_devices` 获取当前 namespace 下的所有网络设备（lo 除外）
2. 删除 namespace 下的网络设备：
 1. 调用 interface driver 删除 `sg-` 设备
 2. 调用 interface dirver 删除 `qg-` 设备
3. 调用 `Namespace.delete` 删除该 namespace

## `class FipNamespace(namespaces.Namespace)`

```
    def __init__(self, ext_net_id, agent_conf, driver, use_ipv6):
        name = self._get_ns_name(ext_net_id)
        super(FipNamespace, self).__init__(
            name, agent_conf, driver, use_ipv6)

        self._ext_net_id = ext_net_id
        self.agent_conf = agent_conf
        self.driver = driver
        self.use_ipv6 = use_ipv6
        self.agent_gateway_port = None
        self._subscribers = set()
        path = os.path.join(agent_conf.state_path, 'fip-priorities')
        self._rule_priorities = frpa.FipRulePriorityAllocator(path,
                                                              FIP_PR_START,
                                                              FIP_PR_END)
        self._iptables_manager = iptables_manager.IptablesManager(
            namespace=self.get_name(),
            use_ipv6=self.use_ipv6)
        path = os.path.join(agent_conf.state_path, 'fip-linklocal-networks')
        self.local_subnets = lla.LinkLocalAllocator(
            path, constants.DVR_FIP_LL_CIDR)
        self.destroyed = False
```

1. 调用 `_get_ns_name` 获取 namespace 的名称
2. `ext_net_id` 表示 external network 的 id
3. 获取 fip-priorities 的文件地址（*/opt/stack/data/neutron/fip-priorities*）
4. 构造 `FipRulePriorityAllocator` 的实例用于记录 floating ip 的分配
5. 构造该 namesapce 的 `IptablesManager` 实例
6. 确定 `fip-linklocal-networks` 路径 （*/opt/stack/data/neutron/fip-linklocal-networks*）
7. 实例化 `LinkLocalAllocator` 用于为 fpr- 分配 ip 地址

### `def _get_ns_name(cls, ext_net_id)`

```
    @classmethod
    def _get_ns_name(cls, ext_net_id):
        return namespaces.build_ns_name(FIP_NS_PREFIX, ext_net_id)
```

获取 namespace 的全名

### `def get_name(self)`

获取自身 namespace 的名称

### `def get_ext_device_name(self, port_id)`

获取 fg- 网络设备的名称（floating ip gateway）

### `def get_int_device_name(self, router_id)`

获取 fpr- 网络设备的名称

### `def get_rtr_ext_device_name(self, router_id)`

获取 rfp- 网络设备的名称

### `def has_subscribers(self)`

```
    def has_subscribers(self):
        return len(self._subscribers) != 0
```

### `def subscribe(self, external_net_id)`

```
    def subscribe(self, external_net_id):
        is_first = not self.has_subscribers()
        self._subscribers.add(external_net_id)
        return is_first
```

### `def unsubscribe(self, external_net_id)`

```
    def unsubscribe(self, external_net_id):
        self._subscribers.discard(external_net_id)
        return not self.has_subscribers()
```

### `def allocate_rule_priority(self, floating_ip)`

```
    def allocate_rule_priority(self, floating_ip):
        return self._rule_priorities.allocate(floating_ip)
```

为 floating ip 分配一个优先级（这个优先级是指 ip rule 的优先级）

### `def deallocate_rule_priority(self, floating_ip)`

```
    def deallocate_rule_priority(self, floating_ip):
        self._rule_priorities.release(floating_ip)
```

回收分配出去的 ip rule 优先级

### `def _fip_port_lock(self, interface_name)`

```
    @contextlib.contextmanager
    def _fip_port_lock(self, interface_name):
        # Use a namespace and port-specific lock semaphore to allow for
        # concurrency
        lock_name = 'port-lock-' + self.name + '-' + interface_name
        with lockutils.lock(lock_name, common_utils.SYNCHRONIZED_PREFIX):
            try:
                yield
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.error(_LE('DVR: FIP namespace config failure '
                                  'for interface %s'), interface_name)
```

产生一个锁

### `def create_or_update_gateway_port(self, agent_gateway_port)`

1. 调用 `get_ext_device_name` 获取 agent gateway port 的名称
2. 调用 `_fip_port_lock` 生成锁
3. 调用 `subscribe` 判断是否应该创建 agent gateway port
4. 若需要创建，则调用 `_create_gateway_port` 创建 agent gateway port
5. 若不需要创建，则调用 `_update_gateway_port` 更新 agent gateway port

### `def _create_gateway_port(self, ex_gw_port, interface_name)`

1. 调用 `get_name` 获取当前 namespace 的名称
2. 调用 interface driver plug 创建网络设备 fg-
3. 调用 `IPWrapper.get_devices` 获取当前 namespace 下的所有设备
4. 若该 namespace 下存在不同于该 agent gateway port 的 fg- 设备，则调用 interface driver unplug 删除这些 fg- 设备（这表明：在每个 fip- namesapce 中，只能存在一个 fg- 设备用来当做 agent gateway）
5. 调用 interface driver init_l3 方法设备刚才创建的 agent gateway port 的 ip 地址
6. 执行 `sysctl -w net.ipv4.conf.fg-xxxxx.proxy_arp=1` 让该 fg- 设备可以执行 arp proxy 功能

### `def _update_gateway_port(self, agent_gateway_port, interface_name)`

1. 调用 `_check_for_gateway_ip_change` 判断 agent gateway port 的 ip 是否发生了变化
2. 若发生了变化，则调用 `_update_gateway_route` 更新关于该 agent gateway 的 route

### ` def _check_for_gateway_ip_change(self, new_agent_gateway_port)`

根据更新数据，判断 agent gateway port 的 ip 是否发生了变化

### `def _update_gateway_route(self, agent_gateway_port, interface_name, tbl_index)`

1. 调用 `get_name` 获取该 namespace 名称
2. 调用 `IPDevice` 描述该 agent gateway port
3. 调用 `ip_lib.send_ip_addr_adv_notif` 来 arp 通知，告诉周围设备 agent gateway ip 地址的变更
4. 若该 agent gateway port 所在的 subnet 存在 gateway，则：
 1. 若 agent gateway port 的 gateway ip 不在 subnet 内，则调用 `IPDevice.route.add_route` 增加 route 的记录
 2. 若 agent gateway port 的 gateway ip 在 subnet 内，则调用 `_add_default_gateway_for_fip` 增加 route 的记录
5. 若该 agent gateway port 所在的 subnet 不存在 gateway，则：
 1. 则删除之前关于该 port 的 gateway route 的记录

### `def _add_default_gateway_for_fip(self, gw_ip, ip_device, tbl_index)`

1. 若未指明 ip route 的 table，则调用 `get_fip_table_indexes` 获取非 'local', 'default', 'main' 的 ip route table，并在这些所有的 table 中，都增加一个 gateway ip 的 route 记录
3. 若指明了 ip route 的 table，则在该 table 中增加一个 gateway ip 的 route 记录

### `def get_fip_table_indexes(self, ip_version)`

1. 执行 ip rule list，获取所有的 ip route table
2. 获取非 'local', 'default', 'main' 的 table

### `def create(self)`

1. 调用 `Namespace.create` 完成 namespace 的创建
2. 调用 `ip_lib.set_ip_nonlocal_bind` 执行 `sysctl -w net.ipv4.ip_nonlocal_bind=1`
3. 增加一个 iptabels 规则如下：`-A neutron-l3-agent-PREROUTING -j CT --notrack`

### `def delete(self)`

调用 `_detele` 实现

### `def _delete(self)`

1. 调用 `IPWrapper.get_devices` 获取当前 namespace 下的所有网络设备（lo 除外）
2. 删除 namespace 下的网络设备：
 1. 调用 `IPWrapper.del_veth` 删除 `rfp-` veth 设备
 2. 调用 interface dirver 删除 `fg-` 设备
3. 调用 `Namespace.delete` 删除该 namespace

### `def create_rtr_2_fip_link(self, ri)`

1. 调用 `get_rtr_ext_device_name` 获取  rfp- 设备的名称
2. 调用 `get_int_device_name` 获取 fpr- 设备的名称
3. 调用 `get_name` 获取该 namespace 的 name
4. 为 fpr- 和 rfp- 设备分配一对 ip 地址
5. 利用 `IPDevice` 来描述这对设备
6. 调用 `IPWrapper.add_veth` 创建这对设备
7. 为这对设备设定 mtu
8. 启动这对设备
9. 调用 `_add_cidr_to_device` 为这对设备各自增加 ip 地址
10. 调用 `_add_rtr_ext_route_rule_to_route_table` 增加 fip- 中的 ip rule，
11. 为 rfp- 设备增加 gateway route：
```
[root@node1 ~]# ip netns exec qrouter-61eaacf9-d4e0-4202-bac9-321da0ceaa69 ip route show table 16
default via 169.254.106.115 dev rfp-61eaacf9-d 
```

### `def _add_cidr_to_device(self, device, ip_cidr)`

为设备增加 Ip 地址

### `def _add_rtr_ext_route_rule_to_route_table(self, ri, fip_2_rtr, fip_2_rtr_name)`

1. 调用 `_update_gateway_route` 更新 route 数据
2. 通过 `IPRule` 增加一条 rule：`2852022899:	from all iif fpr-61eaacf9-d lookup 2852022899`

```
[root@node1 ~]# ip netns exec fip-6c9852c3-7a5b-4b9c-a279-b9098257a0dd ip route list table 2852022899
default via 172.16.100.1 dev fg-efbf14c6-dc 
```

### `def scan_fip_ports(self, ri)`

*scan system for any existing fip ports*

## 辅助方法

*neutron/agent/l3/namespace.py*

### `def build_ns_name(prefix, identifier)`

构造 namespace 名称

### `def get_prefix_from_ns_name(ns_name)`

从一个 namespace 名称中获得前缀（该 namespace 的类型）

### `def get_id_from_ns_name(ns_name)`

从一个 namespace 名称中获得 id

### `def check_ns_existence(f)`

修饰器，判断一个 namespace 是否存在，若存在，则调用 f 方法