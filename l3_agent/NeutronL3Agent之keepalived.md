# Neutron L3 Agent 之 keepalived

*neutron/agent/linux/keepalived.py*

* 参考：

[ keepalive配置文件详解 ](http://www.cnblogs.com/along1226/p/5027838.html)
[理解 OpenStack 高可用（HA）（2）：Neutron L3 Agent HA 之 虚拟路由冗余协议（VRRP）](http://www.cnblogs.com/sammyliu/p/4692081.html)
[ keepalived原理及配置段的说明 ](http://blog.csdn.net/chenlvzhou/article/details/41208487)

## `class KeepalivedVipAddress(object)`

VRRP VIP 地址的描述

```
class KeepalivedVipAddress(object):
    """A virtual address entry of a keepalived configuration."""

    def __init__(self, ip_address, interface_name, scope=None):
        self.ip_address = ip_address
        self.interface_name = interface_name
        self.scope = scope

    def __eq__(self, other):
        return (isinstance(other, KeepalivedVipAddress) and
                self.ip_address == other.ip_address)

    def __str__(self):
        return '[%s, %s, %s]' % (self.ip_address,
                                 self.interface_name,
                                 self.scope)

    def build_config(self):
        result = '%s dev %s' % (self.ip_address, self.interface_name)
        if self.scope:
            result += ' scope %s' % self.scope
        return result
```

## `class KeepalivedVirtualRoute(object)`

一条路由记录

```
class KeepalivedVirtualRoute(object):
    """A virtual route entry of a keepalived configuration."""

    def __init__(self, destination, nexthop, interface_name=None,
                 scope=None):
        self.destination = destination
        self.nexthop = nexthop
        self.interface_name = interface_name
        self.scope = scope

    def build_config(self):
        output = self.destination
        if self.nexthop:
            output += ' via %s' % self.nexthop
        if self.interface_name:
            output += ' dev %s' % self.interface_name
        if self.scope:
            output += ' scope %s' % self.scope
        return output
```

## `class KeepalivedInstanceRoutes(object)`

```
class KeepalivedInstanceRoutes(object):
    def __init__(self):
        self.gateway_routes = []
        self.extra_routes = []
        self.extra_subnets = []

    def remove_routes_on_interface(self, interface_name):
        self.gateway_routes = [gw_rt for gw_rt in self.gateway_routes
                               if gw_rt.interface_name != interface_name]
        # NOTE(amuller): extra_routes are initialized from the router's
        # 'routes' attribute. These routes do not have an interface
        # parameter and so cannot be removed via an interface_name lookup.
        self.extra_subnets = [route for route in self.extra_subnets if
                              route.interface_name != interface_name]

    @property
    def routes(self):
        return self.gateway_routes + self.extra_routes + self.extra_subnets

    def __len__(self):
        return len(self.routes)

    def build_config(self):
        return itertools.chain(['    virtual_routes {'],
                               ('        %s' % route.build_config()
                                for route in self.routes),
                               ['    }'])
```

这个是用来管理 `KeepalivedVirtualRoute` 的。


## `class KeepalivedInstance(object)`

```
    def __init__(self, state, interface, vrouter_id, ha_cidrs,
                 priority=HA_DEFAULT_PRIORITY, advert_int=None,
                 mcast_src_ip=None, nopreempt=False,
                 garp_master_delay=GARP_MASTER_DELAY):
        self.name = 'VR_%s' % vrouter_id

        if state not in VALID_STATES:
            raise InvalidInstanceStateException(state=state)

        self.state = state
        self.interface = interface
        self.vrouter_id = vrouter_id
        self.priority = priority
        self.nopreempt = nopreempt
        self.advert_int = advert_int
        self.mcast_src_ip = mcast_src_ip
        self.garp_master_delay = garp_master_delay
        self.track_interfaces = []
        self.vips = []
        self.virtual_routes = KeepalivedInstanceRoutes()
        self.authentication = None
        self.primary_vip_range = get_free_range(
            parent_range=constants.PRIVATE_CIDR_RANGE,
            excluded_ranges=[constants.METADATA_CIDR,
                             constants.DVR_FIP_LL_CIDR] + ha_cidrs,
            size=PRIMARY_VIP_RANGE_SIZE)
```

1. `vrouter_id`：VRID（一个组内的 VRID 是一样的）
2. `interface`：ha port name
3. `state`：当前 ha port 处于的状态（master、backup、fault）
4. `priority`：VRRP 优先级
5. `nopreempt`：是否是抢占式
6. `advert_int`：VRRP 报文发送时间间隔（默认为 2s）
7. `mcast_src_ip`：发送多播包的地址，如果不设置默认使用绑定网卡的primary ip
8. `garp_master_delay`：在切换到master状态后，延迟进行gratuitous ARP请求
9. `track_interfaces`：跟踪接口
10. `vips`：发送的VRRP包里不包含的IP地址，为减少回应VRRP包的个数。在网卡上绑定的IP地址比较多的时候用。

### `def set_authentication(self, auth_type, password)`

配置 ha 的认证方式

### `def add_vip(self, ip_cidr, interface_name, scope)`

创建一个 `KeepalivedVipAddress` 来描述 vip

### `def remove_vips_vroutes_by_interface(self, interface_name)`

通过 interface 名称来删除一个 vip 的记录，同时删除与该 interface 有关的 route 记录

### `def remove_vip_by_ip_address(self, ip_address)`

删除一个 vip 记录

### `def get_existing_vip_ip_addresses(self, interface_name)`

获取该 interface 上的 vip 地址

### `def _build_track_interface_config(self)`

设定跟踪接口，设置额外的监控，里面任意一块网卡出现问题，都会进入故障(FAULT)状态

### `def get_primary_vip(self)`

根据 VRID 获取一个 primary vip（这个是当前 VRRP 组的 vip）

### `def _build_vips_config(self)`

生成 `virtual_ipaddress` 的配置

### `def _build_virtual_routes_config(self)`

生成 `virtual_routes` 的配置

### `def build_config(self)`

生成 `vrrp_instance` 的配置

## `class KeepalivedConf(object)`

```
class KeepalivedConf(object):
    """A keepalived configuration."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.instances = {}

    def add_instance(self, instance):
        self.instances[instance.vrouter_id] = instance

    def get_instance(self, vrouter_id):
        return self.instances.get(vrouter_id)

    def build_config(self):
        config = ['global_defs {',
                  '    notification_email_from %s' % KEEPALIVED_EMAIL_FROM,
                  '    router_id %s' % KEEPALIVED_ROUTER_ID,
                  '}'
                  ]

        for instance in self.instances.values():
            config.extend(instance.build_config())

        return config

    def get_config_str(self):
        """Generates and returns the keepalived configuration.

        :return: Keepalived configuration string.
        """
        return '\n'.join(self.build_config())
```

这个类用来生成整个 keepalived 的配置

## `class KeepalivedManager(object)`

```
    def __init__(self, resource_id, config, process_monitor, conf_path='/tmp',
                 namespace=None):
        self.resource_id = resource_id
        self.config = config
        self.namespace = namespace
        self.process_monitor = process_monitor
        self.conf_path = conf_path
```

1. `resource_id` : router id
2. `config`：`KeepalivedConf` 实例
3. `namespace` : qrouter- namespace
4. `conf_path` : keepalived 配置文件存放位置

### `def get_conf_dir(self)`

获取当前 router 的 配置文件地址

### `def get_full_config_file_path(self, filename, ensure_conf_dir=True)`

获取 filename 的全路径

### `def _output_config_file(self)`

为该 router 生成 `keepalived.conf` 

### `def _safe_remove_pid_file(pid_file)`

删除 pid file

### `def get_vrrp_pid_file_name(self, base_pid_file)`

```
    def get_vrrp_pid_file_name(self, base_pid_file):
        return '%s-vrrp' % base_pid_file
```

### `def get_conf_on_disk(self)`

读取配置内容

### `def spawn(self)`

1. 调用 `_output_config_file` 生成配置文件
2. 调用 `get_process` 创建 `ProcessManager` 实例，管理 keepalived 进程
3. 调用 `_get_vrrp_process` 创建 `ProcessManager` 实例 管理 vrrp 子进程
4. 启动 keepalived 进程
5. 添加对 keepalived 进程的监视

### `def get_process(self)`

创建一个 `ProcessManager` 实例

### `def _get_vrrp_process(self, pid_file)`

创建一个 `ProcessManager` 实例

### `def disable(self)`

停止 keepalived 进程

### `def _get_keepalived_process_callback(self, vrrp_pm, config_path)`

生成要运行的 keepalived 的名利











