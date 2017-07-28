# Neutron Ovs Agent 之 LocalVlanManager

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/vlanmanager.py*

*存储 vlan 的信息，方便管理。*

## `class LocalVLANMapping(object)`

```
class LocalVLANMapping(object):
    def __init__(self, vlan, network_type, physical_network, segmentation_id,
                 vif_ports=None):
        self.vlan = vlan
        self.network_type = network_type
        self.physical_network = physical_network
        self.segmentation_id = segmentation_id
        self.vif_ports = vif_ports or {}
        # set of tunnel ports on which packets should be flooded
        self.tun_ofports = set()

    def __str__(self):
        return ("lv-id = %s type = %s phys-net = %s phys-id = %s" %
                (self.vlan, self.network_type, self.physical_network,
                 self.segmentation_id))

    def __eq__(self, other):
        return all(hasattr(other, a) and getattr(self, a) == getattr(other, a)
                   for a in ['vlan',
                             'network_type',
                             'physical_network',
                             'segmentation_id',
                             'vif_ports'])

    def __hash__(self):
        return id(self)
```


## `class LocalVlanManager(object)`

```
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(LocalVlanManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'mapping'):
            self.mapping = {}
```

只会有一个 `LocalVlanManager` 的实例


```
    def __contains__(self, key):
        return key in self.mapping

    def __iter__(self):
        for value in list(self.mapping.values()):
            yield value
```

```
    def items(self):
        for item in self.mapping.items():
            yield item
```

```
    def add(self, net_id, vlan, network_type, physical_network,
            segmentation_id, vif_ports=None):
        if net_id in self.mapping:
            raise MappingAlreadyExists(net_id=net_id)
        self.mapping[net_id] = LocalVLANMapping(
            vlan, network_type, physical_network, segmentation_id, vif_ports)
```

增加一个 vlan 信息的记录

```
    def get_net_uuid(self, vif_id):
        for network_id, vlan_mapping in self.mapping.items():
            if vif_id in vlan_mapping.vif_ports:
                return network_id
        raise VifIdNotFound(vif_id=vif_id)
```

通过 vif_id 获得 network_id

```
    def get(self, net_id):
        try:
            return self.mapping[net_id]
        except KeyError:
            raise MappingNotFound(net_id=net_id)

    def pop(self, net_id):
        try:
            return self.mapping.pop(net_id)
        except KeyError:
            raise MappingNotFound(net_id=net_id)
```