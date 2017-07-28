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

**_default_cookie 代表了对当前 bridge flow 操作的 cookie 值**

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

调用 ovs-ofctl 执行添加、删除、修改流表的动作。

例如：

```
ovs-ofctl add-flow ovs-switch "table=0, dl_src=01:00:00:00:00:00/01:00:00:00:00:00, actions=drop"
ovs-ofctl add-flow ovs-switch "table=0, dl_dst=01:80:c2:00:00:00/ff:ff:ff:ff:ff:f0, actions=drop"
```

### `def add_flow(self, **kwargs)`

调用 ovs-ofctl add-flow 来增加流表

### `def mod_flow(self, **kwargs)`

调用 ovs-ofctl mod-flow 来修改流表

### `def delete_flows(self, **kwargs)`

调用 ovs-ofctl  del-flow 来删除该 bridge 的流表记录

### `def dump_flows_for(self, **kwargs)`

根据参数调用 ovs-ofctl dump-flows 命令查询该 bridge 上的流表。

### `def dump_flows_for_table(self, table)`

查询该 bridge 上某个流表内的记录

### `def dump_all_flows(self)`

查询改 bridge 上的所有流表记录

### `def deferred(self, **kwargs)`

构造一个 `DeferredOVSBridge` 实例

### `def add_tunnel_port(self, port_name, remote_ip, local_ip, tunnel_type=p_const.TYPE_GRE, vxlan_udp_port=p_const.VXLAN_UDP_PORT, dont_fragment=True, tunnel_csum=False)`

增加一个 tunnel 类型的接口。

如同执行如下命令：

```
# ovs-vsctl add-port br1 vx1 -- set interface vx1 type=vxlan options:remote_ip=192.168.146.136
```

参考：[搭建基于Open vSwitch的VxLAN隧道实验 ](http://www.sdnlab.com/5365.html)

### `def add_patch_port(self, local_name, remote_name)`

为当前的 bridge 增加一个 patch port

```
ovs-vsctl \
           -- add-port br0 patch-ovs-1 \
           -- set interface patch0 type=patch options:peer=patch-ovs-2 \
           -- add-port br1 patch-ovs-2 \
           -- set interface patch1 type=patch options:peer=patch-ovs-1
```

### `def get_iface_name_list(self)`

获取该 bridge 上所有的 interface 名称

### `def get_port_name_list(self)`

获取该 bridge 上所有的 port 名称

### `def get_port_stats(self, port_name)`

通过获取 interface 的 `statistics` 属性来用作 Port 的状态

### `def get_xapi_iface_id(self, xs_vif_uuid)`

调用 xe 命令

### `def get_ports_attributes(self, table, columns=None, ports=None, check_error=True, log_errors=True, if_exists=False)`

通过读取数据库中的 table，获取指定 ports 的属性（column）。

### `def get_vif_ports(self, ofport_filter=None)`

获取 VIF port，并用 `VifPort` 封装，并且过滤掉在 ofport_filter 中声明的 port。

### `def portid_from_external_ids(self, external_ids)`

在 interface 的 external_ids 的属性中获取 iface_id 或者 xs-vif-uuid

### `def get_vif_port_to_ofport_map(self)`

构造一个映射。`{iface_id:ofport}`

### `def get_vif_port_set(self)`

获取有效的 vif port 集合（以 `iface_id` 标识 vif port）。

### `def get_port_tag_dict(self)`

构造一个 port 的名称与 vlan tag 的集合

### `def _check_ofport(port_id, port_info)`

通过检查 Interface 的 ofport 判断该 port 是够正常

### `def get_vifs_by_ids(self, port_ids)`

通过 port_id 构造该 port 封装 `VifPort`（批量获取）

### `def get_vif_port_by_id(self, port_id)`

通过 port_id 构造该 port 封装 `VifPort`（单个获取）

### `def delete_ports(self, all_ports=False)`

若 all_ports 为真则删除所有 port
若为假则删除 vif port

### `def get_local_port_mac(self)`

获取该 bridge 的 local port 的 mac 地址（br-ex 的 local port 为 br-ex）

### `def set_controllers_connection_mode(self, connection_mode)`

设定该 bridge controller 的 connection_mode

### `def _set_egress_bw_limit_for_port(self, port_name, max_kbps, max_burst_kbps)`

设定该 interface 的 `ingress_policing_rate` 和 `ingress_policing_burst`

### `def create_egress_bw_limit_for_port(self, port_name, max_kbps, max_burst_kbps)`

直接调用 `_set_egress_bw_limit_for_port`

### `def get_egress_bw_limit_for_port(self, port_name)`

获取该 interface 的 `ingress_policing_rate` 和 `ingress_policing_burst`

### `def delete_egress_bw_limit_for_port(self, port_name)`

设定该 interface 的 `ingress_policing_rate` 和 `ingress_policing_burst` 为0


## `class DeferredOVSBridge(object)`

```
class DeferredOVSBridge(object):
    '''Deferred OVSBridge.

    This class wraps add_flow, mod_flow and delete_flows calls to an OVSBridge
    and defers their application until apply_flows call in order to perform
    bulk calls. It wraps also ALLOWED_PASSTHROUGHS calls to avoid mixing
    OVSBridge and DeferredOVSBridge uses.
    This class can be used as a context, in such case apply_flows is called on
    __exit__ except if an exception is raised.
    This class is not thread-safe, that's why for every use a new instance
    must be implemented.
    '''
    ALLOWED_PASSTHROUGHS = 'add_port', 'add_tunnel_port', 'delete_port'

    def __init__(self, br, full_ordered=False,
                 order=('add', 'mod', 'del')):
        '''Constructor.

        :param br: wrapped bridge
        :param full_ordered: Optional, disable flow reordering (slower)
        :param order: Optional, define in which order flow are applied
        '''

        self.br = br
        self.full_ordered = full_ordered
        self.order = order
        if not self.full_ordered:
            self.weights = dict((y, x) for x, y in enumerate(self.order))
        self.action_flow_tuples = []

    def __getattr__(self, name):
        if name in self.ALLOWED_PASSTHROUGHS:
            return getattr(self.br, name)
        raise AttributeError(name)

    def add_flow(self, **kwargs):
        self.action_flow_tuples.append(('add', kwargs))

    def mod_flow(self, **kwargs):
        self.action_flow_tuples.append(('mod', kwargs))

    def delete_flows(self, **kwargs):
        self.action_flow_tuples.append(('del', kwargs))

    def apply_flows(self):
        action_flow_tuples = self.action_flow_tuples
        self.action_flow_tuples = []
        if not action_flow_tuples:
            return

        if not self.full_ordered:
            action_flow_tuples.sort(key=lambda af: self.weights[af[0]])

        grouped = itertools.groupby(action_flow_tuples,
                                    key=operator.itemgetter(0))
        itemgetter_1 = operator.itemgetter(1)
        for action, action_flow_list in grouped:
            flows = list(map(itemgetter_1, action_flow_list))
            self.br.do_action_flows(action, flows)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.apply_flows()
        else:
            LOG.exception(_LE("OVS flows could not be applied on bridge %s"),
                          self.br.br_name)
```

## `def generate_random_cookie()`

```
def generate_random_cookie():
    return uuid.uuid4().int & UINT64_BITMASK
```

## `def _build_flow_expr_str(flow_dict, cmd)`

构建 ovs-ofctl 命令中的流表。






