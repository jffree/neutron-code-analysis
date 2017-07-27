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

对 `OvsdbIdl` 和 command 的封装

```
class BaseOVS(object):

    def __init__(self):
        self.vsctl_timeout = cfg.CONF.ovs_vsctl_timeout
        self.ovsdb = ovsdb.API.get(self)
```

`ovs_vsctl_timeout` 在 `dhcp_agent.ini` 和 `l3_agent.ini` 中都有设定：`ovs_vsctl_timeout = 10`。指的是 ovs-vsctl 命令的超时时间。
`ovsdb`：`OvsdbIdl` 的实例 

### `def add_manager(self, connection_uri)`

调用 ovsdb 增加 manager

### `def get_manager(self)`

调用 ovsdb 获取 manager

### `def remove_manager(self, connection_uri)`

调用 ovsdb 删除 manager

### `def add_bridge(self, bridge_name, datapath_type=constants.OVS_DATAPATH_SYSTEM)` 

调用 ovsdb 增加 bridge，并返回以 `OVSBridge` 封装的 bridge

### `def delete_bridge(self, bridge_name)`

调用 ovsdb 删除 bridge

### `def bridge_exists(self, bridge_name)`

调用 ovsdb 判断 bridger 是否存在

### `def port_exists(self, port_name)`

调用 ovsdb 查询 Port，判断 port 是否存在

### `def get_bridge_for_iface(self, iface)`

调用 ovsdb 根据接口名称获取其所在的 bridge

### `def get_bridges(self)`

获取 bridge 列表

### `def get_bridge_external_bridge_id(self, bridge)`

获取 bridge 的 bridge-id。

相当于执行命令：`ovs-vsctl br-get-external-id br-int bridge-id`

### `def set_db_attribute(self, table_name, record, column, value, check_error=False, log_errors=True)`

设置 ovsdb 中某些别的记录值


### `def clear_db_attribute(self, table_name, record, column)`

调用 ovsdb 清除某个表中某个记录的某个属性的值

### `def db_get_val(self, table, record, column, check_error=False, log_errors=True)`

调用 ovsdb 获取某个表中某个记录的某个属性的值

### `def config(self)`

属性方法

读取 Open_vSwitch 表中的记录

### `def capabilities(self)`

属性方法。

```
{
    'datapath_types': [system],
    'iface_types': [u'geneve', u'gre', u'internal', u'ipsec_gre', u'lisp', u'patch', u'stt', u'system', u'tap', u'vxlan'],
}
```

构造这个字典。

## `class OVSBridge(BaseOVS)`

对名称为 name 的 bridge 的封装

```
    def __init__(self, br_name, datapath_type=constants.OVS_DATAPATH_SYSTEM):
        super(OVSBridge, self).__init__()
        self.br_name = br_name
        self.datapath_type = datapath_type
        self._default_cookie = generate_random_cookie()
```

### `def default_cookie(self)`

属性方法，返回 `self._default_cookie`

### `def set_agent_uuid_stamp(self, val)`

```
    def set_agent_uuid_stamp(self, val):
        self._default_cookie = val
```

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

### `def create(self, secure_mode=False)`

创建一个以 `self.name` 为名称的 bridge，并设置 fail mode 为 `secure`

### `def destroy(self)`

删除以 `self.name` 为名称的 bridge

### `def set_controller(self, controllers)`

为该 bridge 设置 controller

### `def del_controller(self)`

为该 bridge 删除 controller

### `def get_controller(self)`

读取该 bridge 的 controller

### `def _set_bridge_fail_mode(self, mode)`

设置该 bridge 的 fail mode

### `def set_secure_mode(self)`

将该 bridge 的 fail mode 设置为 security

### `def set_standalone_mode(self):`

将该 bridge 的 fail mode 设置为 standalone

### `def set_protocols(self, protocols)`

设置该 bridge 的 protocols 属性

执行如下命令：

```
ovs-vsctl get Bridge br-int protocols
```

返回值：

```
["OpenFlow10", "OpenFlow13"]
```

### `def _get_port_ofport(self, port_name)`

获取一个接口的 ofport。

```
ovs-vsctl get Interface br-ex ofport
65534
```

### `def get_port_ofport(self, port_name)`

将该 port 的 interface 的 ofport 作为自己的 ofport

### `def add_port(self, port_name, *interface_attr_tuples)`

为该 Bridge 增加 port，并设置 port 对应 Interface 的属性

### `def replace_port(self, port_name, *interface_attr_tuples)`

删除该 bridge 上名称为 port_name 的 port
重新增加名称为 port_name 的 port
设置该 Port 的 Interface 的属性

### `def delete_port(self, port_name)`

删除该 bridge 上的一个 port

### `def run_ofctl(self, cmd, args, process_input=None)`

运行 `ovs-ofctl` 的命令。

### `def count_flows(self)`

通过运行 `ovs-ofctl dump-flows self.name` 统计该 bridge 上流表的数量

### `def remove_all_flows(self)`

通过运行 `ovs-ofctl del-flows self.name` 删除该 bridge 上所有的流表

### `def get_datapath_id(self)`

获取该 bridge 的 datapath_id

### `def do_action_flows(self, action, kwargs_list)`


















## `def generate_random_cookie()`

```
def generate_random_cookie():
    return uuid.uuid4().int & UINT64_BITMASK
```

## `def _build_flow_expr_str(flow_dict, cmd)`








