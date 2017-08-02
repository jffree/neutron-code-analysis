# Neutron Ml2 Mechanism Driver 之 l2pop

*neutron/ml2/drivers/l2pop/mech_driver.py*

fdb entity 有两种形式：

* 第一种该 port 启用/停用的时候，这时候的 fdb entity 为：

```
            {
                <uuid>: {
                    ...,
                    'ports': {
                        <ip address>: [ [<mac>, <ip>], ...  ],
                        ...
```

* 第二种该 port update 时，这时候的 fdb entity 为：

```
            { 'chg_ip': {
                '<uuid>': {
                    '<agent1-IP>': {
                        'before': [ [<mac>, <ip>], ... ],
                        'after' : [ [<mac>, <ip>], ... ],
                    },
                    '<agent2-IP>': {
                        'before': ...
```



## `class L2populationMechanismDriver(api.MechanismDriver)`

```
    def __init__(self):
        super(L2populationMechanismDriver, self).__init__()
        self.L2populationAgentNotify = l2pop_rpc.L2populationAgentNotifyAPI()
```

`L2populationAgentNotifyAPI` 是一个 RPC Client，Server endpoint 是 `OVSNeutronAgent` （在 `OVSNeutronAgent.setup_rpc` 中初始化 ）

### `def initialize(self)`

```
    def initialize(self):
        LOG.debug("Experimental L2 population driver")
        self.rpc_ctx = n_context.get_admin_context_without_session()
```

### `def check_vlan_transparency(self, context)`

```

    def check_vlan_transparency(self, context):
        """L2population driver vlan transparency support."""
        return True
```

### `def update_port_precommit(self, context)`

检查当前的更新操作是否正确（若一个 port 为 active 状态，则不能更新 port 的 mac address）。

### `def update_port_postcommit(self, context)`

1. 调用 `l3_hamode_db.is_ha_router_port` 判断 port 是否是 ha 资源，若是的话则不做任何操作
2. 调用 `_get_diff_ips` 获取 port 更新后的 ip 变化，下面分情况进行处理：
3. 若该 port 的 ip/mac 发生变化，则调用 `_fixed_ips_changed`，构造 update fdb entity 并发送广播消息
4. 若 port 的 `device_owner` 为 `DEVICE_OWNER_DVR_INTERFACE`，则：
 1. 若 port 的状态为 `ACTIVE`，则调用 `update_port_up` 创建 fdb entity，并发送广播消息（告诉大家，这个 port 启用了）
 2. 若 port 的状态为 `DOWN`，则调用 `_get_agent_fdb` 创建一个 fdb enetity，并调用 `L2populationAgentNotify.remove_fdb_entries` 发送广播消息（告诉大家这个 Port 停用了）
5. 如果该 port 绑定的 host 发生了变化，且状态由 active 转变为 down，则调用 `_get_agent_fdb` 创建一个 fdb enetity，并调用 `L2populationAgentNotify.remove_fdb_entries` 发送广播消息（告诉大家这个 Port 停用了）
6. 若该 port 的状态由 active 转变为 down，则调用 `_get_agent_fdb` 创建一个 fdb enetity，并调用 `L2populationAgentNotify.remove_fdb_entries` 发送广播消息（告诉大家这个 Port 停用了）
7. 若该 port 的状态由 down 转变为 active，则调用 `update_port_up` 创建 fdb entity，并发送广播消息（告诉大家，这个 port 启用了）

### `def _get_diff_ips(self, orig, port)`

* `orig`：port 的原数据
* `port`：port 更新后的数据

获取 Port 资源进行更新操作后 ip 的变化

### `def update_port_up(self, context)`

1. 调用 `l2pop_db.get_agent_by_host` 根据 host 获取 agent 的数据库记录
2. 调用 `l2pop_db.get_agent_network_active_port_count` 获取与 host 绑定的 port 个数
3. 调用 `l2pop_db.get_agent_ip` 获取 agent 的 ip 地址
4. 获取与该 port 绑定的 segment，调用 `_validate_segment` 验证 `network type` 的正确性
5. 调用 `_get_fdb_entries_template` 构造一个 fdb 的表项
6. 若是该 agent 刚启动，或者该 agent 上的第一个 port 刚被创建，则：
 1. 调用 `_create_agent_fdb` 创建一个 fdb 表（记录别的 agent 上面的 port 信息）
 2. 调用 `L2populationAgentNotify.add_fdb_entries`通过 RPC Clinet 通知该 l2 agent 建立 fdb 表
7. 若该 port 不是 dvr 和 ha 端口，则调用 `_get_port_fdb_entries` 为该 port 创建一个 fdb 记录
8. 调用 `L2populationAgentNotify.add_fdb_entries` 发送广播消息，告诉其他 l2 agent 有新的 fdb 记录产生

### `def _validate_segment(self, segment, port_id, agent)`

1. 调用 `l2pop_db.get_agent_l2pop_network_types` 获取 agent 中的 `l2pop_network_types` 数据，若该数据为空，则获取 `tunnel_types` 数据（用来获取 agent 的网络类型）
2. 若上面获得的 network type 与 segment 中的 `network_type` 不一致则返回 false，一致则返回 true

### `def _get_fdb_entries_template(cls, segment, agent_ip, network_id)`

```
    @classmethod
    def _get_fdb_entries_template(cls, segment, agent_ip, network_id):
        return {
            network_id:
                {'segment_id': segment['segmentation_id'],
                 'network_type': segment['network_type'],
                 'ports': {agent_ip: []}}}
```

构造 FDB——Forwarding DataBase 的表项

### `def _create_agent_fdb(self, session, agent, segment, network_id)`

1. 创建一个 fdb 表 `agent_fdb_entries`
1. 调用 `l2pop_db.get_distributed_active_network_ports` 获取该 network 上的用作 dvr 的 port
2. 调用 `l2pop_db.get_nondistributed_active_network_ports` 获取非 dvr、非 ha 的 Port
3. 调用 `_get_tunnels` 构造 agent （物理机的 Ip）的 fdb 表项
4. 调用 `_get_port_fdb_entries` 构造一个 port 的 fdb 表项
5. 用刚才创建的 agent 和 port 的 fdb 表项更新到 fdb 表中

### `def _get_tunnels(self, tunnel_network_ports, exclude_host)`

构造 agent 的路由表

### `def _get_port_fdb_entries(self, port)`

构造一个 port 的 fdb 表项

### `def _get_agent_fdb(self, segment, port, agent_host)`

构造 agent 上有关该 port 的 fdb 。

### `def _fixed_ips_changed(self, context, orig, port, diff_ips)`

构造一个 update fdb entity，并调用 `L2populationAgentNotify.update_fdb_entries` 发送 RPC 广播消息

### `def update_port_down(self, context)`





## `class L2populationAgentNotifyAPI(object)`

*neutron/plugins/ml2/drivers/l2pop/rpc.py*

RPC Client

RPC Server endpint 为 `OVSNeutronAgent` （在 `OVSNeutronAgent.setup_rpc` 中初始化 ）

```
    def __init__(self, topic=topics.AGENT):
        self.topic = topic
        self.topic_l2pop_update = topics.get_topic_name(topic,
                                                        topics.L2POPULATION,
                                                        topics.UPDATE)
        target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(target)
```

### `def _notification_fanout(self, context, method, fdb_entries)`

发送广播消息

### `def _notification_host(self, context, method, fdb_entries, host)`

发送非广播消息

### `def add_fdb_entries(self, context, fdb_entries, host=None)`

调用 Server 端的 `add_fdb_entries` 方法

若 host 不为 None，则调用 `_notification_host` 发送定向消息
若 host 为 None，则调用 `_notification_fanout` 发送广播消息

### `def remove_fdb_entries(self, context, fdb_entries, host=None)`

调用 Server 端的 `remove_fdb_entries` 方法

若 host 不为 None，则调用 `_notification_host` 发送定向消息
若 host 为 None，则调用 `_notification_fanout` 发送广播消息

### `def update_fdb_entries(self, context, fdb_entries, host=None)`

调用 Server 端的 `update_fdb_entries` 方法

若 host 不为 None，则调用 `_notification_host` 发送定向消息
若 host 为 None，则调用 `_notification_fanout` 发送广播消息