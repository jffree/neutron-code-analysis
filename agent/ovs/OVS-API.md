# Ovs Api

*neutron/agent/ovsdb/api.py*

这个模块里面定义的都是 ovs 操作的抽象类。我们一个个分析。

## `class API(object)`

```
@six.add_metaclass(abc.ABCMeta)
class API(object):
    def __init__(self, context):
        self.context = context
```

### `def get(context, iface_name=None)`

**这个方法用来导入真正的访问 ovs 的 API 接口**

```
    @staticmethod
    def get(context, iface_name=None):
        """Return the configured OVSDB API implementation"""
        iface = importutils.import_class(
            interface_map[iface_name or cfg.CONF.OVS.ovsdb_interface])
        return iface(context)
```

`ovsdb_interface` 就在本模块中定义，默认为 `native`，对应的类为：`neutron.agent.ovsdb.impl_idl.OvsdbIdl`，这个类正好是 `API` 的子类。

我们就直接分析这个类就可以了。

## `class OvsdbIdl(api.API)`

*neutron/agent/ovsdb/impl_idl.py*

```
    ovsdb_connection = connection.Connection(cfg.CONF.OVS.ovsdb_connection,
                                             cfg.CONF.ovs_vsctl_timeout,
                                             'Open_vSwitch')

    def __init__(self, context):
        super(OvsdbIdl, self).__init__(context)
        OvsdbIdl.ovsdb_connection.start()
        self.idl = OvsdbIdl.ovsdb_connection.idl
```

`ovsdb_connection` 用于连接 ovsdb 数据库，在本模块中定义，默认为：`tcp:127.0.0.1:6640`

`ovs_vsctl_timeout` ovs-vsctl 命令的超时时间，默认为 10

启动与 ovsdb server 的数据、命令交流

### `def _tables(self)`

获取 ovsdb 的所有 table

### `def _ovs(self)`

获取数据库中 `Open_vSwitch` 表的第一行记录

### `def transaction(self, check_error=False, log_errors=True, **kwargs)`

构造一个 `NeutronOVSDBTransaction` 对象

```
    def transaction(self, check_error=False, log_errors=True, **kwargs):
        return NeutronOVSDBTransaction(self, OvsdbIdl.ovsdb_connection,
                                       self.context.vsctl_timeout,
                                       check_error, log_errors)
```

### `def add_manager(self, connection_uri)`

创建一个 `AddManagerCommand` 对象

### `def get_manager(self)`

创建一个 `GetManagerCommand` 对象

### `def remove_manager(self, connection_uri)`

创建一个 `RemoveManagerCommand` 对象

### `def add_br(self, name, may_exist=True, datapath_type=None)`

创建一个 `AddBridgeCommand` 对象

### `def del_br(self, name, if_exists=True)`

创建一个 `DelBridgeCommand` 对象

### `def br_exists(self, name)`

创建一个 `BridgeExistsCommand` 对象

### `def port_to_br(self, name)`

创建一个 `PortToBridgeCommand` 对象

### `def iface_to_br(self, name)`

创建一个 `InterfaceToBridgeCommand` 对象

### `def list_br(self)`

创建一个 `ListBridgesCommand` 对象

### `def br_get_external_id(self, name, field)`

创建一个 `BrGetExternalIdCommand` 对象

### `def br_set_external_id(self, name, field, value)`

创建一个 `BrSetExternalIdCommand` 对象

### `def db_create(self, table, **col_values)`

创建一个 `DbCreateCommand` 对象

### `def db_destroy(self, table, record)`

创建一个 `DbDestroyCommand` 对象

### `def db_set(self, table, record, *col_values)`

创建一个 `DbSetCommand` 对象

### `def db_clear(self, table, record, column)`

创建一个 `DbClearCommand` 对象

### `def db_get(self, table, record, column)`

创建一个 `DbGetCommand` 对象

### `def db_list(self, table, records=None, columns=None, if_exists=False)`

创建一个 `DbListCommand` 对象

### `def db_find(self, table, *conditions, **kwargs)`

创建一个 `DbFindCommand` 对象

### `def set_controller(self, bridge, controllers)`

创建一个 `SetControllerCommand` 对象

### `def del_controller(self, bridge)`

创建一个 `DelControllerCommand` 对象

### `def get_controller(self, bridge)`

创建一个 `GetControllerCommand` 对象

### `def set_fail_mode(self, bridge, mode)`

创建一个 `SetFailModeCommand` 对象

### `def add_port(self, bridge, port, may_exist=True)`

创建一个 `AddPortCommand` 对象

### `def del_port(self, port, bridge=None, if_exists=True)`

创建一个 `DelPortCommand` 对象

### `def list_ports(self, bridge)`

创建一个 `ListPortsCommand` 对象

### `def list_ifaces(self, bridge)`

创建一个 `ListIfacesCommand` 对象