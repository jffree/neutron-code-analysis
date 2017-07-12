# Neutron dhcp 辅助类

## `class DictModel(dict)`

*neutron/agent/linux/dhcp.py*

将 dict 类型的变量转化为 `DicModel` 格式。例如： 

```
src = {'a':{'b':1,'c':2}, 'd': 3, 'e':[4,5,6], 'f':(7,8)} 

dst = DictModel(src)

sdst = DictModel({'b':1,'c':2})
sdst['b'] == 1
sdst['b'] == 2

dst['a'] == sdst
dst['d'] == 3
dst['e'] == [4,5,6]
dst['f'] == (7,8)

```
## `class NetModel(DictModel)`

*neutron/agent/linux/dhcp.py*

```
    def __init__(self, d):
        super(NetModel, self).__init__(d)

        self._ns_name = "%s%s" % (NS_PREFIX, self.id)

    @property
    def namespace(self):
        return self._ns_name
```

## `class NetworkCache(object)`

*neutron/agent/dhcp/agent.py*

用于记录当前 dhcp 服务所管理的网络资源。

### `def __init__(self)`

```
    def __init__(self):
        self.cache = {}
        self.subnet_lookup = {}
        self.port_lookup = {}
        self.deleted_ports = set()
```

### `def put(self, network)`

将一个 network 的相关信息（id，subnet，port）保存在当前的实例中。

### `def remove(self, network)`

删除当前缓存中的 network 资源的记录

### `def get_network_by_id(self, network_id)`

根据 network id 获取该网络资源的信息

### `def get_network_by_subnet_id(self, subnet_id)`

通过 subnet id 获取其所在的 netwokr 的信息

### `def get_network_by_port_id(self, port_id)`

通过 port id 获取其所在的 netwokr 的信息

### `def get_network_ids(self)`

获取当前缓存中保存的所有网络的 id

### `def get_port_ids(self, network_ids=None)`

根据 network ids 获取其下面的所有的 port 的 id。

若是 `network_ids` 为空的话，则获取所有的 port 的 id。

### `def remove_port(self, port)`

删除缓存中关于该 port 的记录

### `def get_port_by_id(self, port_id)`

根据 port id 获取该 port 的信息

### `def get_state(self)`

获取当前缓存的所有 network、subnet、port 的数量

### `def is_port_message_stale(self, payload)`

* `playload` 为 port 的信息

若是 playload 包含的 port 信息相对于当前缓存中的 port 的信息是陈旧信息的话，则返回 True。





















