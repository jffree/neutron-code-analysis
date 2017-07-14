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




















