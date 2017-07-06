# Neutron ipam 之 辅助类

*neutron/ipam/sunet_alloc.py*

ipam 的辅助类

## `class SubnetPoolHelper(object)`

### `def ip_version_subnetpool_quota_unit(self, ip_version)`

```
    def ip_version_subnetpool_quota_unit(self, ip_version):
        return self._PREFIX_VERSION_INFO[ip_version]['quota_units']
```
### `def default_min_prefixlen(self, ip_version)`

获取某版本的ip的默认最小 prefixlen

### `def default_max_prefixlen(self, ip_version)`

获取某版本的ip的默认最大 prefixlen

### `def wildcard(self, ip_version)`

```
    def wildcard(self, ip_version):                                                                                                                                    
        return self._PREFIX_VERSION_INFO[ip_version]['wildcard']

```

### `def validate_min_prefixlen(self, min_prefixlen, max_prefixlen)`

验证子网池的 `min_prefixlen` 属性

```
    def validate_min_prefixlen(self, min_prefixlen, max_prefixlen):
        if min_prefixlen < 0:
            raise n_exc.UnsupportedMinSubnetPoolPrefix(prefix=min_prefixlen,
                                                       version=4)                                                                                                      
        if min_prefixlen > max_prefixlen:
            raise n_exc.IllegalSubnetPoolPrefixBounds(
                                             prefix_type='min_prefixlen',
                                             prefixlen=min_prefixlen,
                                             base_prefix_type='max_prefixlen',
                                             base_prefixlen=max_prefixlen)
```

### `def validate_max_prefixlen(self, prefixlen, ip_version)`

验证子网池的 `max_prefixlen` 属性

```

    def validate_max_prefixlen(self, prefixlen, ip_version):
        max = self._PREFIX_VERSION_INFO[ip_version]['max_prefixlen']
        if prefixlen > max:
            raise n_exc.IllegalSubnetPoolPrefixBounds(
                                            prefix_type='max_prefixlen',
                                            prefixlen=prefixlen,
                                            base_prefix_type='ip_version_max',
                                            base_prefixlen=max)
```

### `def validate_default_prefixlen(self, min_prefixlen, max_prefixlen, default_prefixlen)`

验证子网池的 `default_prefixlen` 是否合法

```
    def validate_default_prefixlen(self,
                                   min_prefixlen,
                                   max_prefixlen,
                                   default_prefixlen):
        if default_prefixlen < min_prefixlen:
            raise n_exc.IllegalSubnetPoolPrefixBounds(
                                             prefix_type='default_prefixlen',
                                             prefixlen=default_prefixlen,
                                             base_prefix_type='min_prefixlen',
                                             base_prefixlen=min_prefixlen)
        if default_prefixlen > max_prefixlen:
            raise n_exc.IllegalSubnetPoolPrefixBounds(
                                             prefix_type='default_prefixlen',
                                             prefixlen=default_prefixlen,
                                             base_prefix_type='max_prefixlen',                                                                                         
                                             base_prefixlen=max_prefixlen)
```


## `class IpamSubnet(driver.Subnet)`

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