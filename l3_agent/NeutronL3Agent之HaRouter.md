# Nuetron L3 Agent HaRouter

*neutron/agent/l3/ha_router.py*

## `class HaRouterNamespace(namespaces.RouterNamespace)`

```
class HaRouterNamespace(namespaces.RouterNamespace):
    """Namespace for HA router.

    This namespace sets the ip_nonlocal_bind to 0 for HA router namespaces.
    It does so to prevent sending gratuitous ARPs for interfaces that got VIP
    removed in the middle of processing.
    """
    def create(self):
        super(HaRouterNamespace, self).create()
        # HA router namespaces should not have ip_nonlocal_bind enabled
        ip_lib.set_ip_nonlocal_bind_for_namespace(self.name)
```

## `class HaRouter(router.RouterInfo)`

```
class HaRouter(router.RouterInfo):
    def __init__(self, state_change_callback, *args, **kwargs):
        super(HaRouter, self).__init__(*args, **kwargs)

        self.ha_port = None
        self.keepalived_manager = None
        self.state_change_callback = state_change_callback
```

### `def create_router_namespace_object(self, router_id, agent_conf, iface_driver, use_ipv6)`

```
    def create_router_namespace_object(
            self, router_id, agent_conf, iface_driver, use_ipv6):
        return HaRouterNamespace(
            router_id, agent_conf, iface_driver, use_ipv6)
```

ha 没有单独的 namespace，也是放在 qrouter- namespace 中的

### `def ha_priority(self)`

```
    @property
    def ha_priority(self):
        return self.router.get('priority', keepalived.HA_DEFAULT_PRIORITY)
```

VRRP 优先级

### `def ha_vr_id(self)`

```
    @property
    def ha_vr_id(self):
        return self.router.get('ha_vr_id')
```

VRRP ID

### `def ha_state(self)`

```
    @property
    def ha_state(self):
        ha_state_path = self.keepalived_manager.get_full_config_file_path(
            'state')
        try:
            with open(ha_state_path, 'r') as f:
                return f.read()
        except (OSError, IOError):
            LOG.debug('Error while reading HA state for %s', self.router_id)
            return None
```

通过读取 ha 数据文件的内容，判断当前 ha router 的状态


### `def ha_state(self, new_state)`

```
    @ha_state.setter
    def ha_state(self, new_state):
        ha_state_path = self.keepalived_manager.get_full_config_file_path(
            'state')
        try:
            with open(ha_state_path, 'w') as f:
                f.write(new_state)
        except (OSError, IOError):
            LOG.error(_LE('Error while writing HA state for %s'),
                      self.router_id)
```

设定 ha state

### `def ha_namespace(self)`

```
    @property
    def ha_namespace(self):
        return self.ns_name
```

### `def initialize(self, process_monitor)`

1. 调用父类的 initialize 处理
2. 获取 ha port，若没有则退出
3. 调用 `_init_keepalived_manager` 初始化 keepalived 配置
4. 调用 `ha_network_added` 创建 ha port，初始化 ip
5. 调用 `update_initial_state` 将 router 更新为 ha master 状态
6. 调用 `spawn_state_change_monitor` 启动 `neutron-keepalived-state-change` 进程

### ` def _init_keepalived_manager(self, process_monitor)`

1. 生成 `KeepalivedManager` 实例
2. 调用 `get_ha_device_name` 获取 ha interface 的名称
3. 创建一个 `keepalived.KeepalivedInstance` 实例
4. 若配置文件中设定了 `ha_vrrp_auth_password`，则调用 `KeepalivedInstance.set_authentication` 设定 vrrp 的认证方式

### `def enable_keepalived(self)`

启动 keepalived

### `def disable_keepalived(self)`

停止 keepalived，删除配置信息

### `def ha_network_added(self)`

创建 ha port，为该 ha port 配置 ip 地址

### `def ha_network_removed(self)`

删除 ha port

### `def _get_primary_vip(self)`

```
    def _get_primary_vip(self):
        return self._get_keepalived_instance().get_primary_vip()
```

### `def update_in_get_primary_vipitial_state(self, callback)`

1. 调用 `IPDevice` 描述 ha port
2. 调用 `_get_primary_vip` 将该 router 设置为 master
3. 回调处理，记录 router 更新的信息

### `def spawn_state_change_monitor(self, process_monitor)`

1. 调用 `_get_state_change_monitor_process_manager` 创建 `neutron-keepalived-state-change` 的管理器
2. 启动 `neutron-keepalived-state-change` 进程

### `def _get_state_change_monitor_process_manager(self)`

```
    def _get_state_change_monitor_process_manager(self):
        return external_process.ProcessManager(
            self.agent_conf,
            '%s.monitor' % self.router_id,
            self.ha_namespace,
            default_cmd_callback=self._get_state_change_monitor_callback())
```

### `def _get_state_change_monitor_callback(self)`

创建需要启动 `neutron-keepalived-state-change` 的命令

### `def get_ha_device_name(self)`

获取本路由上的 ha port 名称

### `def _add_vips(self, port, interface_name)`

```
    def _add_vips(self, port, interface_name):
        for ip_cidr in common_utils.fixed_ip_cidrs(port['fixed_ips']):
            self._add_vip(ip_cidr, interface_name)
```

### `def _add_vip(self, ip_cidr, interface, scope=None)`

1. 调用 `_get_keepalived_instance` 获取该 router 的描述
2. 为该 Instance 增加一个 vip 记录

### `def _get_keepalived_instance(self)`

获取本 router 在 keepalived 中的 instance 描述

### `def _remove_vip(self, ip_cidr)`

删除该 router instance 上的一个 vips 记录

### `def _clear_vips(self, interface)`

清空关于该 Interface 上的 vips 记录

### `def _get_cidrs_from_keepalived(self, interface_name)`

1. 调用 `_get_keepalived_instance` 获取该 router 的 instance 
2. 调用 `instance.get_existing_vip_ip_addresses` 获取 vips 中记录的该 interface 上的 ip

### `def get_router_cidrs(self, device)`

```
    def get_router_cidrs(self, device):
        return set(self._get_cidrs_from_keepalived(device.name))
```

### `def routes_updated(self, old_routes, new_routes)`

创建 `KeepalivedVirtualRoute` 来更新 Keepalived 中的 route 记录

### `def _add_default_gw_virtual_route(self, ex_gw_port, interface_name)`

为该 router 的 keepalived instance 中增加 gateway 记录

### `def _add_extra_subnet_onlink_routes(self, ex_gw_port, interface_name)`

为该 router 的 keepalived instance 中增加额外的 route 记录

### `def _should_delete_ipv6_lladdr(self, ipv6_lladdr)`

对于 Ipv6 地址的处理

```
    def _should_delete_ipv6_lladdr(self, ipv6_lladdr):
        """Only the master should have any IP addresses configured.
        Let keepalived manage IPv6 link local addresses, the same way we let
        it manage IPv4 addresses. If the router is not in the master state,
        we must delete the address first as it is autoconfigured by the kernel.
        """
        manager = self.keepalived_manager
        if manager.get_process().active:
            if self.ha_state != 'master':
                conf = manager.get_conf_on_disk()
                managed_by_keepalived = conf and ipv6_lladdr in conf
                if managed_by_keepalived:
                    return False
            else:
                return False
        return True
```

### `def _disable_ipv6_addressing_on_interface(self, interface_name)`

```
    def _disable_ipv6_addressing_on_interface(self, interface_name):
        """Disable IPv6 link local addressing on the device and add it as
        a VIP to keepalived. This means that the IPv6 link local address
        will only be present on the master.
        """
        device = ip_lib.IPDevice(interface_name, namespace=self.ha_namespace)
        ipv6_lladdr = ip_lib.get_ipv6_lladdr(device.link.address)

        if self._should_delete_ipv6_lladdr(ipv6_lladdr):
            device.addr.flush(n_consts.IP_VERSION_6)

        self._remove_vip(ipv6_lladdr)
        self._add_vip(ipv6_lladdr, interface_name, scope='link')
```

### `def add_floating_ip(self, fip, interface_name, device)`

调用 `_add_vip` 完成操作

### `def remove_floating_ip(self, device, ip_cidr)`

1. 调用 `_remove_vip` 移除该 floating ip 的记录
2. 调用父类的 `remove_floating_ip` 完成后续处理

### `def internal_network_updated(self, interface_name, ip_cidrs)`

1. 调用 `_clear_vips` 清除该 interface 上的 vip 的记录
2. 调用 `_disable_ipv6_addressing_on_interface` 处理该 port 上的 ipv6
3. 调用 `_add_vip` 增肌阿盖 Interface 的新的 vip 记录

### `def _plug_ha_router_port(self, port, name_getter, prefix)`

创建新的 router port，增加该 port 的  vip 记录

### `def internal_network_added(self, port)`

调用 `_plug_ha_router_port` 进行处理

### `def internal_network_removed(self, port)`

1. 调用父类的 `internal_network_removed` 完成前序处理
2. 调用 `_clear_vips` 删除该 router port 的 vip 记录

### `def destroy_state_change_monitor(self, process_monitor)`

销毁 `neutron-keepalived-state-change` 进程

### `def _gateway_ports_equal(port1, port2)`

判断两个 port 是否相等

### `def external_gateway_added(self, ex_gw_port, interface_name)`

1. 调用 `RouterInfo._plug_external_gateway` 完成 gateway 的添加
2. 调用 `_add_gateway_vip` 记录 gateway 的 ip
3. 处理 ipv6 事项

### `def external_gateway_updated(self, ex_gw_port, interface_name)`

1. 调用 `RouterInfo._plug_external_gateway` 完成 gateway port 的更新
2. 清理之前的关于该 gateway 的 vip 记录，增加新的 vip 记录

### `def external_gateway_removed(self, ex_gw_port, interface_name)`

1. 调用 `_clear_vips` 完成 vip 的清理
2. 若该 router 为 ha master，则调用 `RouterInfo.external_gateway_removed` 清理 gateway
3. 若该 router 为 ha backup，则直接删除该 port

### `def delete(self, agent)`

1. 调用 `destroy_state_change_monitor` 停止 `neutron-keepalived-state-change` 进程
2. 调用 `disable_keepalived` 停止 keepalived 进程
3. 调用 `ha_network_removed` 删除 ha port
4. 调用父类的 delete 完成其他处理

### `def process(self, agent)`

在之前处理的基础上，若是含有 ha port，则启动 keepalived 进程

### `def enable_radvd(self, internal_ports=None)`

```
    @common_utils.synchronized('enable_radvd')
    def enable_radvd(self, internal_ports=None):
        if (self.keepalived_manager.get_process().active and
                self.ha_state == 'master'):
            super(HaRouter, self).enable_radvd(internal_ports)
```

只会在 ha master router 上启动 radvd 服务