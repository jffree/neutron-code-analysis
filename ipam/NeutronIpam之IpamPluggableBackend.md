# Neutron ipam 之 IpamPluggableBackend

*neutron/db/ipam_pluggable_backend.py*

```
class IpamBackendMixin(db_base_plugin_common.DbBasePluginCommon)
class IpamPluggableBackend(ipam_backend_mixin.IpamBackendMixin)
```

我们就从 `IpamBackendMixin` 看起

## `class IpamBackendMixin(db_base_plugin_common.DbBasePluginCommon)`

### `def validate_pools_with_subnetpool(self, subnet)`

在创建子网时，可能会指定从 subnet_pool 中分配子网的 ip，这时会调用该方法验证请求是否合法。

1. 调用 `validators.is_attr_set` 判断 subnet 属性中是否包含 `allocation_pools` 和 `cidr`。
2. 若 subnet 属性中同时包含这两个属性时，则会引发异常。

### `def generate_pools(self, cidr, gateway_ip)`

调用 `ipam_utils.generate_pools` 实现

### `def pools_to_ip_range(ip_pools)`

将地址池用 `IPRange` 来描述。











## `class IpamPluggableBackend(ipam_backend_mixin.IpamBackendMixin)`