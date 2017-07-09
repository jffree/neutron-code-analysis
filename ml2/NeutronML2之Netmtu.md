# Neutron Ml2 之 Netmtu

## extension

*neutron/extensions/netmtu.py*

`class Netmtu(extensions.ExtensionDescriptor)`

## 无 Model

## WSIG 实现

*neutron/db/netmtu_db.py*

## `class Netmtu_db_mixin(object)`

```
class Netmtu_db_mixin(object):
    """Mixin class to add network MTU support to db_base_plugin_v2."""

    def _extend_network_dict_mtu(self, network_res, network_db):
        # don't use network_db argument since MTU is not persisted in database
        network_res[netmtu.MTU] = utils.get_deployment_physnet_mtu()
        return network_res

    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attributes.NETWORKS, ['_extend_network_dict_mtu'])
```

*neutron/plugins/common/utils.py*

```
def get_deployment_physnet_mtu():
    """Retrieves global physical network MTU setting.

    Plugins should use this function to retrieve the MTU set by the operator
    that is equal to or less than the MTU of their nodes' physical interfaces.
    Note that it is the responsibility of the plugin to deduct the value of
    any encapsulation overhead required before advertising it to VMs.
    """
    return cfg.CONF.global_physnet_mtu
```

*/etc/neutron/neutron.conf*

```
# MTU of the underlying physical network. Neutron uses this value to calculate
# MTU for all virtual network components. For flat and VLAN networks, neutron
# uses this value without modification. For overlay networks such as VXLAN,
# neutron automatically subtracts the overlay protocol overhead from this
# value. Defaults to 1500, the standard value for Ethernet. (integer value)
# Deprecated group/name - [ml2]/segment_mtu
#global_physnet_mtu = 1500
```