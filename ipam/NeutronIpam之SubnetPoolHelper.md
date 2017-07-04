# Neutron ipam 之 SubnetPoolHelper

*neutron/ipam/sunet_alloc.py*

ipam 的辅助类

## `class SubnetPoolHelper(object)`

### `def ip_version_subnetpool_quota_unit(self, ip_version)`

```
    def ip_version_subnetpool_quota_unit(self, ip_version):
        return self._PREFIX_VERSION_INFO[ip_version]['quota_units']
```


















