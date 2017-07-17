# Nuetron Agent 之 ip_lib

*neutron/agent/linux/ip_lib.py*

实现了 linux 上 ip 命令的操作。

* 这个模块主要构造了两种类：
 1. 以 `IpCommandBase` 为基类的子类。这些类用来构造具体的想要执行的命令（比如 `ip netns`），但是不执行。
 2. 以 `SubProcessBase` 为基类的子类。这些类用来将上面构造的具体的命令以一个单独的子进程来启动。
 3. `IpCommandBase` 的子类有三种：`IPWrapper` `IPDevice` `IPRule` `IPRoute`
  1. `IPWrapper` 负责 `IpNetnsCommand` 的执行
  2. `IPDevice` 负责 `IpLinkCommand` `IpAddrCommand` `IpRouteCommand` `IpNeighCommand` 的执行
  3. `IPRule` 负责 `IpRuleCommand` 的执行
  4. `IPRoute` 负责 `IpRouteCommand` 的执行

## `class SubProcessBase(object)`

### `def __init__(self, namespace=None, log_fail_as_error=True)`

```
    def __init__(self, namespace=None,
                 log_fail_as_error=True):
        self.namespace = namespace
        self.log_fail_as_error = log_fail_as_error
        try:
            self.force_root = cfg.CONF.ip_lib_force_root
        except cfg.NoSuchOptError:
            # Only callers that need to force use of the root helper
            # need to register the option.
            self.force_root = False
```

我找了找配置文件，还真没有 `ip_lib_force_root` 这个选项

### `def _as_root(self, options, command, args, use_root_namespace=False)`

```
    def _as_root(self, options, command, args, use_root_namespace=False):
        namespace = self.namespace if not use_root_namespace else None

        return self._execute(options, command, args, run_as_root=True,
                             namespace=namespace,
                             log_fail_as_error=self.log_fail_as_error)
```

确定要在那个命名空间下**以 root 的身份**执行子进程。（root 既是 None，无需命名空间）

### `def _execute(cls, options, command, args, run_as_root=False, namespace=None, log_fail_as_error=True)`

类方法

```
    @classmethod
    def _execute(cls, options, command, args, run_as_root=False,
                 namespace=None, log_fail_as_error=True):
        opt_list = ['-%s' % o for o in options]
        ip_cmd = add_namespace_to_cmd(['ip'], namespace)
        cmd = ip_cmd + opt_list + [command] + list(args)
        return utils.execute(cmd, run_as_root=run_as_root,
                             log_fail_as_error=log_fail_as_error)
```

* 参数说明：
 1. `options`：命令执行的选项
 2. `command`：要执行的命令
 3. `args`：命令执行的参数（选项时可选的，参数是必须的）
 4. `run_as_root`：是否以 root 权限执行
 5. `namespace`：命令执行的命名空间
 6. `log_fail_as_error`：命令执行出错时，是否记录到 Log 中

调用 `utils.execute` 完成命令的执行

### `def _run(self, options, command, args)`

```
    def _run(self, options, command, args):
        if self.namespace:
            return self._as_root(options, command, args)
        elif self.force_root:
            # Force use of the root helper to ensure that commands
            # will execute in dom0 when running under XenServer/XCP.
            return self._execute(options, command, args, run_as_root=True,
                                 log_fail_as_error=self.log_fail_as_error)
        else:
            return self._execute(options, command, args,
                                 log_fail_as_error=self.log_fail_as_error)
```

根据不同的情况，设定 `self._execute` 的执行参数

### `def set_log_fail_as_error(self, fail_with_error)`

```
    def set_log_fail_as_error(self, fail_with_error):
        self.log_fail_as_error = fail_with_error
```

### `def get_log_fail_as_error(self)`

```
    def get_log_fail_as_error(self):
        return self.log_fail_as_error
```

### `class IPWrapper(SubProcessBase)`

### `def __init__(self, namespace=None)`

```
    def __init__(self, namespace=None):
        super(IPWrapper, self).__init__(namespace=namespace)
        self.netns = IpNetnsCommand(self)
```

### `def get_devices(self, exclude_loopback=False, exclude_gre_devices=False)`

获取该 namespace 下的网络设备名称，并以 `IPDevice` 包装后返回。

* `exclude_loopback`：是否排除本地回环设备（`lo`）
* `exclude_gre_devices`：是否排除 gre 设备（`gre0` `gretap0`）

相当于执行如下命令：`ip netns exec net0 find /sys/class/net -maxdepth 1 -type l -printf '%f '`

将命令执行的结果以 `IPDevice` 包装后返回。

### `def device(self, name)`

用 `IPDevice` 表示一个在该 namespace 下的一个设备

### `def get_device_by_ip(self, ip)`

根据 ip 地址获取网络设备。

调用 `IpAddrCommand.get_devices_with_ip` 实现，但是只会取第一个设备（不同的网卡能拥有完全相同的 ip 地址）。

返回以 `IPDevice` 包装的网络设备

### `def ensure_namespace(self, name)`

确保名称为 name 的 namespace 存在。若是不存在，则新建一个，并启动其中的回环设备。

### `def add_veth(self, name1, name2, namespace2=None)`

增加一堆 veth 设备，名称为 name1 的在本 namespace 下，名称为 name2 的在 namespace2 下面

执行如下命令：`ip netns exec net0 ip link add tap0 type veth peer name tap1 netns net1`

返回以 `IPDevice` 描述的两格 veth 设备。

### `def add_tuntap(self, name, mode='tap')`

增加一个名称为 name 的 tun/tap 设备

执行如下命令：`ip netns exec net0 ip tuntap add tap-simple mode tap`

返回以 `IPDevice` 描述的 tun/tap 设备

* 参考

[Linux下Tun/Tap设备通信原理](http://www.cnblogs.com/woshiweige/p/4532207.html)
[虚拟网卡 TUN/TAP 驱动程序设计原理](https://www.ibm.com/developerworks/cn/linux/l-tuntap/)
[关于 TCP 并发连接的几个思考题与试验 ](http://blog.csdn.net/solstice/article/details/6579232)

### `def add_macvtap(self, name, src_dev, mode='bridge')`

增加一个名称为 name 的 macvtap 设备，默认的模式为 bridge

执行如下命令：`ip link add link eth0 name macv1 type macvtap mode bridge`

返回以 `IPDevice` 描述的 macvtap 设备

* 参考

[图解几个与Linux网络虚拟化相关的虚拟网卡-VETH/MACVLAN/MACVTAP/IPVLAN ](http://blog.csdn.net/dog250/article/details/45788279)
[Linux 上虚拟网络与真实网络的映射](https://www.ibm.com/developerworks/cn/linux/1312_xiawc_linuxvirtnet/)

### `def del_veth(self, name)`

删除名为 name 的 veth 设备

执行如下命令：`ip link delete tap0`

### `def add_dummy(self, name)`

添加一个名称为 name 的 dummy 类型的网卡（哑网卡只会简单的直接丢弃所有发送给它的数据包）。

执行如下命令：`ip link add dum type dummy`

返回以 `IPDevice` 描述的 dummy 设备

### `def namespace_is_empty(self)`

判断是否当前的 namespace 除了回环设备和 gre 设备外，再无其它设备

### `def garbage_collect_namespace(self)`

如果当前的 namespace 是空的话，则删除此命名空间。

### `def add_device_to_namespace(self, device)`

将一个以 `IPDevice` 描述的网络设备增加到当前的命名空间中。

### `def add_vlan(self, name, physical_interface, vlan_id)`

增加一个 vlan 设备。

执行如下命令：`ip link add link eth0 name v1 type vlan id 34`

返回以 `IPDevice` 描述的 vlan 设备

### `def add_vxlan(self, name, vni, group=None, dev=None, ttl=None, tos=None, local=None, port=None, proxy=False)`

增加一个 vxlan 设备。

* 参数说明：
 * `name`：网卡名称
 * `vni`：vxlan id
 * `group`：多播地址
 * `dev`：物理网卡的名称
 * `ttl`：生存期限
 * `tos`：服务类型（请参考：[IP首部中的服务类型（TOS）](http://www.mamicode.com/info-detail-542445.html)）
 * `local`：设定发出包的 VETP（Vxlan Tunnel End Point） 源 ip 地址 [Vxlan基础理解](http://blog.csdn.net/freezgw1985/article/details/16354897/)
 * `port`：用于声明本地监听 UDP 端口的范围。（在新版的 ip-link 的命令中，这个发生了变化：1. 用 `dstport` 来声明对端的 UDP 端口；2. 使用 `srcport` 来声明本端监听的 UDP 端口的范围）
 * `proxy`：arp proxy 功能（请参考：[配置 L2 Population - 每天5分钟玩转 OpenStack（114）](http://www.cnblogs.com/CloudMan6/p/6072315.html)）

执行如下命令：`ip link add vxlan0 type vxlan id 42 group 239.1.1.1 dev eth0 port 4750 4790 proxy`

### `def get_namespaces(cls)`

获取所有的 namespace。执行命令：`ip netns list`

## `class IpNetnsCommand(IpCommandBase)`

`COMMAND = 'netns'`

### `def exists(self, name)`

`use_helper_for_ns_read`：指明读取 ip namespace 时是否使用 root 权限（默认为 True）。 

执行 `ip -o netns list` 命令，然后查询名字为 name 的 namespace 是否存在

### `def delete(self, name)`

删除名字为 name 的 namespace。执行命令：`ip netns delete net0`

### `def add(self, name)`

增加一个名称为 name 的 namespace。

执行命令：

```
ip netns add net0
ip netns exec net0 sysctl -w net.ipv4.conf.all.promote_secondaries=1
```

关于 sysctl 调整内核参数，请参考：[内核参数说明](http://www.cnblogs.com/tolimit/p/5065761.html)

返回一个以 `IPWrapper` 包装的 namespace

### `def execute(self, cmds, addl_env=None, check_exit_code=True, log_fail_as_error=True, extra_ok_codes=None, run_as_root=False)`

参数同 `utils.execute` 方法里面的参数。

在当前的命名空间下执行 cmd 命令。

## `class IPDevice(SubProcessBase)`

### `def __init__(self, name, namespace=None)`

```
    def __init__(self, name, namespace=None):
        super(IPDevice, self).__init__(namespace=namespace)
        self._name = name
        self.link = IpLinkCommand(self)
        self.addr = IpAddrCommand(self)
        self.route = IpRouteCommand(self)
        self.neigh = IpNeighCommand(self)
```

### `def __eq__(self, other)`

```
    def __eq__(self, other):
        return (other is not None and self.name == other.name
                and self.namespace == other.namespace)
```

### `def __str__(self)`

```
    def __str__(self):
        return self.name
```




## `class IpCommandBase(object)`

`COMMAND = ''`

ip 命令的格式如下：

```
ip [ OPTIONS ] OBJECT { COMMAND | help }
```

这里的 COMMAND 就相当不 OBJECT，代表着你要操作的对象。

### `def __init__(self, parent)`

```
    def __init__(self, parent):
        self._parent = parent
```

### `def _run(self, options, args)`

```
    def _run(self, options, args):
        return self._parent._run(options, self.COMMAND, args)
```


### `def _as_root(self, options, args, use_root_namespace=False)`

```
    def _as_root(self, options, args, use_root_namespace=False):
        return self._parent._as_root(options,
                                     self.COMMAND,
                                     args,
                                     use_root_namespace=use_root_namespace)
```














## `class IpDeviceCommandBase(IpCommandBase)`

```
class IpDeviceCommandBase(IpCommandBase):
    @property
    def name(self):
        return self._parent.name
```

## `class IpLinkCommand(IpDeviceCommandBase)`

`COMMAND = 'link`

link 既是指网络设备的相关操作

### `def delete(self)`

```
    def delete(self):
        self._as_root([], ('delete', self.name))
```

执行删除网络设备的命令。例如：`ip netns qdhcp-ea3928dc-b1fd-4a1a-940e-82b8c55214e6 ip link delete tap13685e28-b0 `

### `def set_address(self, mac_address)`

```
    def set_address(self, mac_address):
        self._as_root([], ('set', self.name, 'address', mac_address))
```

执行设置网络设备网络（mac）地址的命令。例如：`ip netns qdhcp-ea3928dc-b1fd-4a1a-940e-82b8c55214e6 ip link set tap13685e28-b0 00:01:4f:00:15:f1`

### `def set_allmulticast_on(self)`

执行设置网络设备是否支持多播模式的命令。例如：`ip netns qdhcp-ea3928dc-b1fd-4a1a-940e-82b8c55214e6 ip link set tap13685e28-b0 allmulticast on`

设置此参数后，网卡将接收网络中所有的多播数据包

### `def set_mtu(self, mtu_size)`

设置网卡 mtu 的大小。例如：`ip link set tap13685e28-b0 mtu 1400`

### `def set_up(self)`

启动该网卡 `ip link set tap13685e28-b0 up`

### `def set_down(self)`

关闭该网卡 `ip link set tap13685e28-b0 down`

### `def set_netns(self, namespace)`

设置该网卡所在的命名空间。 `ip link set tap13685e28-b0 netns qdhcp-ea3928dc-b1fd-4a1a-940e-82b8c55214e6`

### `def set_name(self, name)`

设置网卡的名称。`ip link set tap13685e28-b0 name tap-simple`

该命令只有在网卡关闭的情况下才能执行成功

### `def set_alias(self, alias_name)`

为网卡设置别名。`ip link set tap13685e28-b0 alias tap-simple`

### `def attributes(self)`

属性方法。相当于执行：`ip netns exec net0 ip -o link show tap13685e28-b0`

-o 选项，意味着命令的输出仅为一行（换行符用 \ 替代）。

调用 `_parse_line` 方法解析 Ip 命令的输出，获取易读的网卡的状态：

* 解析前：

```
ip netns exec net0 ip -o link show veth0

3: veth0@veth1: <BROADCAST,MULTICAST,M-DOWN> mtu 1400 qdisc noqueue state DOWN mode DEFAULT qlen 1000\    link/ether 00:01:4f:00:15:f2 brd ff:ff:ff:ff:ff:ff\    alias veth0
```

* 解析后：

```
{'qlen': 1000, 'qdisc': 'noqueue', 'link/ether': '00:01:4f:00:15:f2', 'mtu': 1400, 'alias': 'veth0', 'state': 'DOWN', 'mode': 'DEFAULT', 'brd': 'ff:ff:ff:ff:ff:ff'}
```

### `def address(self)`

属性方法，获取网卡的网络（mac）地址

### `def state(self)`

属性方法，获取网卡的状态

### `def mtu(self)`

属性方法，获取网卡的 mtu

### `def qdisc(self)`

属性方法，获取网卡的流量的排队准则。

参考：

[ LIUNX下tc流量控制命令详解 ](http://blog.csdn.net/ysdaniel/article/details/7905879)
[Linux 网络堆栈的排队机制](http://blog.jobbole.com/62917/)
[从veth看虚拟网络设备的qdisc](http://www.cnblogs.com/hustcat/p/4025070.html)

### `def qlen(self)`

属性方法，获取网卡 qlen（网络接口传输队列的默认长度）数据。

### `def alias(self)`

获取网卡别名

## `class IpAddrCommand(IpDeviceCommandBase)`

`COMMAND = 'addr'`

### `def add(self, cidr, scope='global', add_broadcast=True)`

为网卡增加 ip 地址。

* 参数说明：
 1. `cidr`：ip 地址（192.168.100.10/24）
 2. `scope`：ip 地址的有效范围（参考 ip-address 命令手册 man ip-address）
 3. `add_broadcast`：是否增加广播地址

相当于执行如下命令：`ip -4 addr add 192.168.100.10/24 scope global dev veth0 brd 192.168.100.255`

### `def delete(self, cidr)`

删除网卡上的 ip 地址。`ip -4 addr del 192.168.100.10/24 dev veth0`

### `def flush(self, ip_version)`

清除网卡上的 ip 地址。`ip -4 addr flush dev veth0`

### `def get_devices_with_ip(self, name=None, scope=None, to=None, filters=None, ip_version=None)`

返回网卡的参数（不同的网卡可能拥有完全相同的 ip 地址）。

* 参数说明：
 1. `name`：网卡名称
 2. `scope`：地址范围
 3. `to`：地址的匹配项
 4. `filters`：其他过滤选项
 5. `ip-version`：ip 版本

`ip -4 addr show veth0 scope global to 192.168.100.10`

结果为：

```
3: veth0@veth1: <BROADCAST,MULTICAST,M-DOWN> mtu 1400 qdisc noqueue state DOWN qlen 1000
    inet 192.168.100.11/24 brd 192.168.100.255 scope global veth0
       valid_lft forever preferred_lft forever
```

则该方法的返回值为：`{'name':'veth0','cidr':'192.168.100.11/24', 'scope':'global', 'dynamic':False, 'tentative':False, 'dadfailed':False}`

### `def list(self, scope=None, to=None, filters=None, ip_version=None)`

调用 `get_devices_with_ip` 返回本网卡的参数

### `def wait_until_address_ready(self, address, wait_time=30)`

在 wait_time 的时间内，一直等待 ip 地址 address 在本网卡上准备好。若是没有准备好，则引发异常

## `class IpNeighCommand(IpDeviceCommandBase)`

`COMMAND = 'neigh'`

构建相邻表（ARP 表）

### `def add(self, ip_address, mac_address)`

增加（替换）一个相邻表项。

执行命令：`ip -4 neigh replace 10.0.0.3 lladdr fe:ee:ff:ff:ff:ff nud permanent dev eth0`

其中，`permanent` 指邻接条目永远有效并且只能由管理员删除。

### `def delete(self, ip_address, mac_address)`

删除一个相邻表项

执行命令：`ip -4 del 10.0.0.3 lladdr fe:ee:ff:ff:ff:ff dev eth0`

### `def show(self, ip_version)`

显示一个网络设备上的相邻表。

执行命令：`ip -4 show dev eth0`

### `def flush(self, ip_version, ip_address)`

清除当前设备的相邻表项。

执行命令：`ip -4 flush to 10.0.0.3`

## `class IPRoute(SubProcessBase)`

```
class IPRoute(SubProcessBase):
    def __init__(self, namespace=None, table=None):
        super(IPRoute, self).__init__(namespace=namespace)
        self.name = None
        self.route = IpRouteCommand(self, table=table)
```

## `class IpRouteCommand(IpDeviceCommandBase)`

**系统中的路由记录是在一个一个的路由表中存在的（路由表在 /etc/iproute2/rt_tables 文件中记录）。最多可以定义 256 个路由表，启动 0、253、254、255 是由 kernel 维护的。**

* linux 系统中，可以自定义从 1－252个路由表，其中，linux系统维护了4个路由表：
 1. 0#表： 系统保留表
 2. 253#表： defulte table 没特别指定的默认路由都放在该表
 3. 254#表： main table 没指明路由表的所有路由放在该表
 4. 255#表： locale table 保存本地接口地址，广播地址、NAT地址 由系统维护，用户不得更改


`IpRouteCommand` 也是以路由表为单位来进行维护的。在没有指明路由表的情况下，默认是对 main 表进行操作的。

```
    COMMAND = 'route'

    def __init__(self, parent, table=None):
        super(IpRouteCommand, self).__init__(parent)
        self._table = table
```

### `def table(self, table)`

返回一个 `IpRouteCommand` 描述的路由表。

### `def _table_args(self, override=None)`

构造 `ip route` 命令的 `table` 选项。

```
    def _table_args(self, override=None):
        if override:
            return ['table', override]
        return ['table', self._table] if self._table else []
```

例如：`ip route show table local` 就是查询 local 表中记录的路由项。

### `def _dev_args(self)`

构造 `ip route` 命令的 `dev` 选项。

```
    def _dev_args(self):
        return ['dev', self.name] if self.name else []
```

例如：`ip route show dev eth0` 就是查询经过 eth0 网卡的路由。

### `def _run_as_root_detect_device_not_found(self, *args, **kwargs)`

处理运行命令时，无法找到 device 的异常

### `def get_gateway(self, scope=None, filters=None, ip_version=None)`

`filters`：之其他的过滤选项

获取本表中，经过本设备转发的网关地址及其 `metric` 属性。

执行命令如下：`ip -4 route show table main dev eno1 scope globle `

命令返回为： `default via 192.168.40.254 proto static metric 100`

方法返回为：`{'gateway':'192.168.40.254','metric':100}`

### `def _parse_routes(self, ip_version, output, **kwargs)`

生成器方法，将 ip route 输出的结果转化为易读的格式。

### `def list_routes(self, ip_version, **kwargs)`

查询路由。

执行命令：`ip -4 router list table main dev eno1 `

调用 `_parse_routes` 对命令结果的数据进行转化。

### `def list_onlink_routes(self, ip_version)`

列出 scope 为 link 的路由。

执行命令：`ip -4 router list table main dev eno1 scope link`

*不过这里面的不带 `src` 是什么鬼？  `list_onlink_routes` 与 `add_onlink_routes` 方法是对应的，因为 `add_onlink_routes` 添加路由表项时，也没有添加 src 属性。*

### `def add_route(self, cidr, via=None, table=None, **kwargs)`

在路由表中增加一个记录。

执行命令如下：`ip -4 route replace 192.168.40.237 via 192.168.40.254 dev eno1 table main src 192.168.40.247 scope global`

### `def add_onlink_route(self, cidr)`

增加一个 scope 为 link 的路由表

执行命令如下：`ip -4 route replace 192.168.40.237 dev eno1 table main scope link`

### `def delete_route(self, cidr, via=None, table=None, **kwargs)`

删除一个路由表项

执行命令如下：`ip -4 route del 192.168.40.237 dev eno1 table main`

### `def delete_onlink_route(self, cidr)`

删除一个 scope 为 link 的路由表项

执行命令如下：`ip -4 route del 192.168.40.237 dev eno1 table main scope link`

### `def add_gateway(self, gateway, metric=None, table=None)`

增加一个网关记录。

执行命令如下：`ip -4 route default via 192.168.40.254 dev eno1 table main matric 100`

### `def delete_gateway(self, gateway, table=None)`

删除默认网关的记录。

执行命令如下：`ip -4 route del default via 192.168.40.254 dev eno1 table main`

### `def flush(self, ip_version, table=None, **kwargs)`

清空某一个路由表的记录。

执行命令如下：`ip -4 flush table main`

## `class IPRule(SubProcessBase)`

```
class IPRule(SubProcessBase):
    def __init__(self, namespace=None):
        super(IPRule, self).__init__(namespace=namespace)
        self.rule = IpRuleCommand(self)
```

## `class IpRuleCommand(IpCommandBase)`

`COMMAND = 'rule'`

### `def list_rules(self, ip_version)`

例如当前策略路由的所有规则。

执行命令：`ip -4 rule show`

命令返回值为：

```
220:	from 192.203.80.0/24 fwmark 0x1 lookup main
```

调用 `_parse_line` 来解析命令的返回值。

解析完成后：

`{'fwmark': '0x1/0xffffffff', 'table': 'main', 'priority': '220', 'type': 'unicast', 'from': '192.203.80.0/24'}`

## `def add_namespace_to_cmd(cmd, namespace=None)`

```
def add_namespace_to_cmd(cmd, namespace=None):
    """Add an optional namespace to the command."""

    return ['ip', 'netns', 'exec', namespace] + cmd if namespace else cmd
```

当 namespace 不为空时，构造类似于下面的命令：`ip netns exec namespce cmd`

### `def _exists(self, ip_version, **kwargs)`

kwargs：包含某个 rule 的属性。判断该 rule 是否存在。

### `def add(self, ip, **kwargs)`

增加一个 rule 记录。

执行命令如下：`ip ru add from 193.233.7.83 nat 192.203.80.144 table 1 pref 320`

### `def delete(self, ip, **kwargs)`

删除一个 rule 记录

执行命令如下：`ip ru del prio 32767`











