# Neutron agent 之 interface

*neutron/agent/linux/interface.py*

linux 系统下的接口驱动，共有四种，分别是：`BridgeInterfaceDriver`、`IVSInterfaceDriver`、`NullDriver`、`OVSInterfaceDriver`。

我们以  `OVSInterfaceDriver` 来进行分析

## `class LinuxInterfaceDriver(object)`

抽象基类

```
    DEV_NAME_LEN = 14
    DEV_NAME_PREFIX = constants.TAP_DEVICE_PREFIX
```

### `def __init__(self, conf)`

```
    DEV_NAME_LEN = 14
    DEV_NAME_PREFIX = constants.TAP_DEVICE_PREFIX

    def __init__(self, conf):
        self.conf = conf
        self._mtu_update_warn_logged = False
```

### `def use_gateway_ips(self)`

属性方法，返回 false

### `def get_device_name(self, port)`

根据 port 中的信息，返回该 port 在 linux 上的名称（*tap921f5a37-3b*）

### `def plug(self, network_id, port_id, device_name, mac_address, bridge=None, namespace=None, prefix=None, mtu=None)`

调用 `ip_lib.device_exists` 判断该网络设备是否存在，若不存在则调用 `plug_new`（在子类中实现），若存在则调用 `set_mtu`（在子类中实现）为该网络设备设定 MTU

### `def check_bridge_exists(self, bridge)`

调用 `ip_lib.device_exists` 检查该网桥是否存在

### `def init_l3(self, device_name, ip_cidrs, namespace=None, preserve_ips=None, clean_connections=False)`

为名称为 device_name 的网络设备确定 ip 地址，并删除之前的 ip 地址





## `class OVSInterfaceDriver(LinuxInterfaceDriver)`

`DEV_NAME_PREFIX = constants.TAP_DEVICE_PREFIX`

### `def __init__(self, conf)`

```
    def __init__(self, conf):
        super(OVSInterfaceDriver, self).__init__(conf)
        if self.conf.ovs_use_veth:
            self.DEV_NAME_PREFIX = 'ns-'
```

`ovs_use_veth`：是否使用 veth 设备作为 ovs 的接口（*dhcp_agent.ini* 和 *l3_agent.ini* 都有这个选项，这里设置为 False。）。

在看这篇文章 [ 用 namspace 隔离 DHCP 服务 - 每天5分钟玩转 OpenStack（90）](http://www.cnblogs.com/CloudMan6/p/5894891.html) 时，看到了以 **ns-** 开头的网卡名称，现在才理解，原来是在这里设定的。

### `def plug_new(self, network_id, port_id, device_name, mac_address, bridge=None, namespace=None, prefix=None, mtu=None)`

在网桥（默认 br-int）上创建（插入新的网卡），设定网卡的 mac 、namespace 、mtu，并激活网卡

1. 调用 `_get_tap_name` 获取 tap 接口名称
2. 若使用 veth 类型，则调用 `IPWrapper.add_veth` 创建网络设备
3. 若不使用 veth 类型，则不作处理
4. 调用 `_ovs_add_port` 将 port 增加到 bridge 中
5. 调用 `ns_dev.link.set_address` 设置 port 的 mac 地址
6. 若不是 veth 类型，还需要将 ovs 创建的 port 增加到相应的 namespace 中
7. 调用 `set_mtu` 设定 port 的 mtu 
8. 若是 veth 类型，还需要激活 tap 网卡

### `def _ovs_add_port(self, bridge, device_name, port_id, mac_address, internal=True)`

在 ovs 的 bridge 上增加一个 port

### `def set_mtu(self, device_name, mtu, namespace=None, prefix=None)`

设定 dhcp port 的 mtu 值（若是采用 veth 类型，还需要设定对端 tap 类型网卡的 mtu）

### `def _get_tap_name(self, dev_name, prefix=None)`

获取 tap 接口名称。（`ovs_use_veth`是否支持 ovs 使用 veth 设备，在`dhcp_agent.ini` 和 `l3_agent.ini` 中都有定义：`ovs_use_veth = False`）

若使用 veth 类型的网络设备。对于 dhcp port 来说，其中一个名称以 `ns-` 开头，另外一个以 `tap` 开头







### `def unplug(self, device_name, bridge=None, namespace=None, prefix=None)`

* 参数说明：
 * `device_name`：接口名称（例如：`tape2976960-b0`）
 * `bridge`：网桥名称（没有声明的话则从配置文件中读取。在 `dhcp_agent.ini` 和 `l3_agent.ini` 中都有定义：`ovs_integration_bridge = br-int`）
 * `namespace`：网络命名空间。这个在 `NetModel` 中被定义（例如 `qdhcp-53a0f128-ab6a-4f3f-b29f-c1afe0697586`）
 * `prefix`：接口名称的前缀

### `def unplug(self, device_name, bridge=None, namespace=None, prefix=None)`

在 bridge 上删除名为 `device_name` 的接口














