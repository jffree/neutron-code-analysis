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


## `class IpNetnsCommand(IpCommandBase)`

`COMMAND = 'netns'`






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

返回网卡的参数。

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






## `def add_namespace_to_cmd(cmd, namespace=None)`

```
def add_namespace_to_cmd(cmd, namespace=None):
    """Add an optional namespace to the command."""

    return ['ip', 'netns', 'exec', namespace] + cmd if namespace else cmd
```

当 namespace 不为空时，构造类似于下面的命令：`ip netns exec namespce cmd`























