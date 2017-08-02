# Neutron Ml2 Mechanism Driver 基类

## `class MechanismDriver(object)`

*抽象基类，定义了 mechanism driver 的框架*

### `def initialize(self)`

### `def create_network_precommit(self, context)`

### `def create_network_postcommit(self, context)`

### `def update_network_precommit(self, context)`

### `def update_network_postcommit(self, context)`

### `def delete_network_precommit(self, context)`

### `def delete_network_postcommit(self, context)`

### `def create_subnet_precommit(self, context)`

### `def create_subnet_postcommit(self, context)`

### `def update_subnet_precommit(self, context)`

### `def update_subnet_postcommit(self, context)`

### `def delete_subnet_precommit(self, context)`

### `def delete_subnet_postcommit(self, context)`

### ` def create_port_precommit(self, context)`

### `def create_port_postcommit(self, context)`

### `def update_port_precommit(self, context)`

### `def update_port_postcommit(self, context)`

### `def delete_port_precommit(self, context)`

### `def delete_port_postcommit(self, context)`

### `def bind_port(self, context)`

### `def _supports_port_binding(self)`

```
    @property
    def _supports_port_binding(self):
        return self.__class__.bind_port != MechanismDriver.bind_port
```

检查子类是否重写了 `bind_port` 方法

### `def check_vlan_transparency(self, context)`

### `def get_workers(self)`

### `def is_host_filtering_supported(cls)`

```
    @classmethod
    def is_host_filtering_supported(cls):
        return (cls.filter_hosts_with_segment_access !=
                MechanismDriver.filter_hosts_with_segment_access)
```

### `def filter_hosts_with_segment_access(self, context, segments, candidate_hosts, agent_getter)`


## `class AgentMechanismDriverBase(api.MechanismDriver)`

*neutron/plugins/ml2/drivers/mech_agent.py*

*抽象基类*

```
@six.add_metaclass(abc.ABCMeta)
class AgentMechanismDriverBase(api.MechanismDriver):
    def __init__(self, agent_type,
                 supported_vnic_types=[portbindings.VNIC_NORMAL]):
        """Initialize base class for specific L2 agent type.

        :param agent_type: Constant identifying agent type in agents_db
        :param supported_vnic_types: The binding:vnic_type values we can bind
        """
        self.agent_type = agent_type
        self.supported_vnic_types = supported_vnic_types
```

### `def initialize(self)`

```
    def initialize(self):
        pass
```

### `def create_port_precommit(self, context)`

```
    def create_port_precommit(self, context):
        self._insert_provisioning_block(context)
```

调用 `_insert_provisioning_block` 为该 port 增加一个 `ProvisioningBlock` 的数据库记录

### `def _insert_provisioning_block(self, context)`

创建 port 资源时，在 neutron-server 端处理完成后，还需要在 dhcp agent 完成进一步的操作才可以使用。
本方法就是在 neutron-server 端完成处理后，创建一个 `ProvisioningBlock` 的数据库记录，直到 dhcp agent 处理完成后，释放这个 block，然后该 port 算就完成了。

### `def update_port_precommit(self, context)`

调用 `_insert_provisioning_block` 为该 port 增加一个 `ProvisioningBlock` 的数据库记录

### `def bind_port(self, context)`

调用 `try_to_bind_segment_for_agent`（openvswitch 在 `OpenvswitchMechanismDriver` 中实现，linuxbridge 在 `SimpleAgentMechanismDriverBase` 中实现） 实现去设定 port 的 binding 属性








## `class SimpleAgentMechanismDriverBase(AgentMechanismDriverBase)`

```
    def __init__(self, agent_type, vif_type, vif_details,
                 supported_vnic_types=[portbindings.VNIC_NORMAL]):
        super(SimpleAgentMechanismDriverBase, self).__init__(
            agent_type, supported_vnic_types)
        self.vif_type = vif_type
        self.vif_details = vif_details
```

### `def try_to_bind_segment_for_agent(self, context, segment, agent)`

1. 调用 `check_segment_for_agent`


### `def check_segment_for_agent(self, segment, agent)`

1. 调用 `get_mappings` 获取 bridge_mapping 的设定值。（各子类实现）
2. 调用 `get_allowed_network_types` 获取 agent 支持的网络类型（各子类实现）
3. 检查 segment 的参数与 agent 的设定是否一致
 
### `def filter_hosts_with_segment_access（self, context, segments, candidate_hosts, agent_getter)`

根据 `check_segment_for_agent` 来确定该 host 是否可以 access。









