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
    def __init__(self, conf):
        self.conf = conf
        self._mtu_update_warn_logged = False
```

### `def use_gateway_ips(self)`

属性方法，返回 false


## `class OVSInterfaceDriver(LinuxInterfaceDriver)`

`DEV_NAME_PREFIX = constants.TAP_DEVICE_PREFIX`

### `def __init__(self, conf)`

```
    def __init__(self, conf):
        super(OVSInterfaceDriver, self).__init__(conf)
        if self.conf.ovs_use_veth:
            self.DEV_NAME_PREFIX = 'ns-'
```

### `def unplug(self, device_name, bridge=None, namespace=None, prefix=None)`

* 参数说明：
 * `device_name`：接口名称（例如：`tape2976960-b0`）
 * `bridge`：网桥名称（没有声明的话则从配置文件中读取。在 `dhcp_agent.ini` 和 `l3_agent.ini` 中都有定义：`ovs_integration_bridge = br-int`）
 * `namespace`：网络命名空间。这个在 `NetModel` 中被定义（例如 `qdhcp-53a0f128-ab6a-4f3f-b29f-c1afe0697586`）
 * `prefix`：接口名称的前缀

1. 调用 `_get_tap_name` 获取真正的接口名称


### `def _get_tap_name(self, dev_name, prefix=None)`

获取真正的接口名称。（`ovs_use_veth`是否支持 ovs 使用 veth 设备，在`dhcp_agent.ini` 和 `l3_agent.ini` 中都有定义：`ovs_use_veth = False`）

### `def unplug(self, device_name, bridge=None, namespace=None, prefix=None)`

在 bridge 上删除名为 `device_name` 的接口














