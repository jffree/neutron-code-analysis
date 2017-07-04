# Neutron ipam 之 辅助类

*neutron/ipam/sunet_alloc.py*

ipam 的辅助类

## `class SubnetPoolHelper(object)`

### `def ip_version_subnetpool_quota_unit(self, ip_version)`

```
    def ip_version_subnetpool_quota_unit(self, ip_version):
        return self._PREFIX_VERSION_INFO[ip_version]['quota_units']
```


### `class IpamSubnet(driver.Subnet)`

```
class IpamSubnet(driver.Subnet):

    def __init__(self,
                 tenant_id,
                 subnet_id,
                 cidr,
                 gateway_ip=None,
                 allocation_pools=None):
        self._req = ipam_req.SpecificSubnetRequest(
            tenant_id,
            subnet_id,
            cidr,
            gateway_ip=gateway_ip,
            allocation_pools=allocation_pools)

    def allocate(self, address_request):
        raise NotImplementedError()

    def deallocate(self, address):
        raise NotImplementedError()

    def get_details(self):                                                                                                                                             
        return self._req
```

比较明显，最重要的是构造了一个 `SpecificSubnetRequest` 的请求












