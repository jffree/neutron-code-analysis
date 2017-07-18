# Neutron Agent Common OVS_LIB

*neutron/agent/common/ovs_lib.py*

实现了 linux 上 ovs 命令的操作。

## 参考

[基于 Open vSwitch 的 OpenFlow 实践](https://www.ibm.com/developerworks/cn/cloud/library/1401_zhaoyi_openswitch/)

## `class VifPort(object)`

```
class VifPort(object):
    def __init__(self, port_name, ofport, vif_id, vif_mac, switch):
        self.port_name = port_name
        self.ofport = ofport
        self.vif_id = vif_id
        self.vif_mac = vif_mac
        self.switch = switch

    def __str__(self):
        return ("iface-id=%s, vif_mac=%s, port_name=%s, ofport=%s, "
                "bridge_name=%s") % (
                    self.vif_id, self.vif_mac,
                    self.port_name, self.ofport,
                    self.switch.br_name)
```

## `class BaseOVS(object)`

```
class BaseOVS(object):

    def __init__(self):
        self.vsctl_timeout = cfg.CONF.ovs_vsctl_timeout
        self.ovsdb = ovsdb.API.get(self)
```

`ovs_vsctl_timeout` 在 `dhcp_agent.ini` 和 `l3_agent.ini` 中都有设定：`ovs_vsctl_timeout = 10`。指的是 ovs-vsctl 命令的超时时间。
 



 



## `class OVSBridge(BaseOVS)`

```
    def __init__(self, br_name, datapath_type=constants.OVS_DATAPATH_SYSTEM):
        super(OVSBridge, self).__init__()
        self.br_name = br_name
        self.datapath_type = datapath_type
        self._default_cookie = generate_random_cookie()
```

### `def default_cookie(self)`

属性方法，返回 `self._default_cookie`

### `def __enter__(self)`

```
    def __enter__(self):
        self.create()
        return self
```

### `def __exit__(self, exc_type, exc_value, exc_tb)`

```
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.destroy()
```
















## `def generate_random_cookie()`

```
def generate_random_cookie():
    return uuid.uuid4().int & UINT64_BITMASK
```










