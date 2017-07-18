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

`ovsdb_interface` 就在本模块重定义，默认为 `native`，对应的类为：`neutron.agent.ovsdb.impl_idl.OvsdbIdl`，这个类正好是 `API` 的子类。

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




























