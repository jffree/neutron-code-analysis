# Neutron Ml2 type driver 之 local

## `class LocalTypeDriver(api.TypeDriver)`

*neutron/plugins/ml2/drivers/type_local.py*

没有做任何的操作

```
class LocalTypeDriver(api.TypeDriver):
    """Manage state for local networks with ML2.

    The LocalTypeDriver implements the 'local' network_type. Local
    network segments provide connectivity between VMs and other
    devices running on the same node, provided that a common local
    network bridging technology is available to those devices. Local
    network segments do not provide any connectivity between nodes.
    """

    def __init__(self):
        LOG.info(_LI("ML2 LocalTypeDriver initialization complete"))

    def get_type(self):
        return p_const.TYPE_LOCAL

    def initialize(self):
        pass

    def is_partial_segment(self, segment):
        return False

    def validate_provider_segment(self, segment):
        for key, value in six.iteritems(segment):
            if value and key != api.NETWORK_TYPE:
                msg = _("%s prohibited for local provider network") % key
                raise exc.InvalidInput(error_message=msg)

    def reserve_provider_segment(self, session, segment):
        # No resources to reserve
        return segment

    def allocate_tenant_segment(self, session):
        # No resources to allocate
        return {api.NETWORK_TYPE: p_const.TYPE_LOCAL}

    def release_segment(self, session, segment):
        # No resources to release
        pass

    def get_mtu(self, physical_network=None):
        pass
```