# Neutron ML2 之 RPC notifier

```
    def _start_rpc_notifiers(self):
        """Initialize RPC notifiers for agents."""
        self.notifier = rpc.AgentNotifierApi(topics.AGENT)
        self.agent_notifiers[const.AGENT_TYPE_DHCP] = (
            dhcp_rpc_agent_api.DhcpAgentNotifyAPI()
        )
```

看代码，有两个部分：分别是 `self.notifier` 和 `self.agent_notifiers`。


## `self.notifier` 是由 `AgentNotifierApi` 来实现：

* 位置：*neutron/plugins/ml2/rpc.py*

* 继承关系：

```
class AgentNotifierApi(dvr_rpc.DVRAgentRpcApiMixin,
                       sg_rpc.SecurityGroupAgentRpcApiMixin,
                       type_tunnel.TunnelAgentRpcApiMixin)
```

从 mixin 我们就可以看出来，这些类都是相互独立的，提供不同的功能，在这里集合在一起是为了统一的使用。

从类的名称我们可以看出，这个类是专门为了 agent 设置的 rpc 消息通知类。

## `self.agent_notifiers` 是由 `AgentSchedulerDbMixin` 来定义

* 位置：*neutron/db/agentschedulers_db.py*

*这一个我们在 NeutronMl2之RPC-agent_notifier*

```
class AgentSchedulerDbMixin(agents_db.AgentDbMixin):
    """Common class for agent scheduler mixins."""

    # agent notifiers to handle agent update operations;
    # should be updated by plugins;
    agent_notifiers = {
        constants.AGENT_TYPE_DHCP: None,
        constants.AGENT_TYPE_L3: None,
        constants.AGENT_TYPE_LOADBALANCER: None,
    }
```

## `class AgentNotifierApi`

* **思路：** 为不同的资源定义不同的 topic，调用 rpc client 的 prepare 方法来更新 client 的 topic 属性，在此基础上发送消息。

### `def network_delete(self, context, network_id)`

* **topic :** `q-agent-notifier-network-delete`
* **method :** `network_delete`

### `port_update(self, context, port, network_type, segmentation_id,                    physical_network)`

* **topic :** `q-agent-notifier-port-update`
* **method :** `port_update`

### `def port_delete(self, context, port_id)`

* **topic :** `q-agent-notifier-port-delete`
* **method :** `port_delete`

### `def network_update(self, context, network)`

* **topic :** `q-agent-notifier-network-update`
* **method :** `network_update`

## `class DVRAgentRpcApiMixin(object)`

### `def dvr_mac_address_update(self, context, dvr_macs)`

* **topic :** `q-agent-notifier-dvr-update`
* **method :** `dvr_mac_address_update`
* **version** : `"1.0"`
* **fanout** : `True`

## `class SecurityGroupAgentRpcApiMixin(object)`

### `def security_groups_rule_updated(self, context, security_groups)`

* **topic :** `q-agent-notifier-security_group-update`
* **method :** `security_groups_rule_updated`
* **version** : `"1.1"`
* **fanout** : `True`

### `def security_groups_member_updated(self, context, security_groups)`

* **topic :** `q-agent-notifier-security_group-update`
* **method :** `security_groups_member_updated`
* **version** : `"1.1"`
* **fanout** : `True`

### `def security_groups_provider_updated(self, context, devices_to_update=None)`

* **topic :** `q-agent-notifier-security_group-update`
* **method :** `security_groups_provider_updated`
* **version** : `"1.1"`
* **fanout** : `True`

## `class TunnelAgentRpcApiMixin(object)`

### `def tunnel_update(self, context, tunnel_ip, tunnel_type)`

* **topic :** `q-agent-notifier-tunnel-update`
* **method :** `tunnel_update`
* **fanout** : `True`

### `def tunnel_delete(self, context, tunnel_ip, tunnel_type)`

* **topic :** `q-agent-notifier-tunnel-delete`
* **method :** `tunnel_delete`
* **fanout** : `True`