# Neutron OvsAgent 之 RPC



## `SecurityGroupAgentRpcCallbackMixin`

*neutron/agent/securitygroups_rpc.py*







## `class L2populationRpcCallBackTunnelMixin(L2populationRpcCallBackMixin)`

*neutron/plugins/ml2/drivers/l2pop/rpc_manager/l2population_rpc.py*


## `class DVRAgentRpcCallbackMixin(object)`

*neutron/api/rpc/handlers/dvr_rpc.py*

```
class DVRAgentRpcCallbackMixin(object):
    """Agent-side RPC (implementation) for plugin-to-agent interaction."""

    def dvr_mac_address_update(self, context, **kwargs):
        """Callback for dvr_mac_addresses update.

        :param dvr_macs: list of updated dvr_macs
        """
        dvr_macs = kwargs.get('dvr_macs', [])
        LOG.debug("dvr_macs updated on remote: %s", dvr_macs)
        self.dvr_agent.dvr_mac_address_update(dvr_macs)
```
