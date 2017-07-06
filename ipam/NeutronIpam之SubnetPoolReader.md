# Neutron Ipam 之 SubnetPoolReader

*neutron/ipam/subnet_alloc.py*

`SubnetPoolReader` 的实例用来描述一个 SubnetPool 的数据库记录

## `class SubnetPoolReader(object)`

### `def __init__(self, subnetpool)`

* `subnetpool`：一个SubnetPool的数据库记录

用一个 `SubnetPoolReader` 的实例来描述一个 SubnetPool 的数据库记录 

### `def _read_prefix_info(self, subnetpool)`

设置该实例的 `default_quota`、`ip_version`、`prefixes` 属性

### `def _compact_subnetpool_prefix_list(self, prefix_list)`

一个 subnetpool 可能有好几个地址池，这些地址池中可能有些可以用一个大的 `cidr` 来表示，这个方法的作用就是将地址池压缩

例如：10.10.10.0/24 可以分为：{10.10.10.0/25,10.10.10.128/25}

### `def _read_id(self, subnetpool)`

获取该子网池数据库的 id，并设置 `self.id` 属性

### `def _read_prefix_bounds(self, subnetpool)`

1. 根据 sunbentpool 的 ip 版本，获取该 subnetpool 的默认最大最小 prefixlen
2. 调用 `_read_prefix_bound` 构造 `min_prefixlen`、`min_prefix` 属性
3. 调用 `_read_prefix_bound` 构造 `max_prefixlen`、`max_prefix` 属性
4. 调用 `_read_prefix_bound` 构造 `default_prefixlen`、`default__prefix` 属性
5. 调用 `validate_min_prefixlen` 验证 `min_prefixlen` 属性是否合法
6. 调用 `validate_max_prefixlen` 验证 `max_prefixlen` 属性是否合法
7. 调用 `validate_default_prefixlen` 验证 `default_prefixlen` 属性是否合法


### `def _read_prefix_bound(self, type, subnetpool, default_bound=None)`

```
    def _read_prefix_bound(self, type, subnetpool, default_bound=None):
        prefixlen_attr = type + '_prefixlen'
        prefix_attr = type + '_prefix'
        prefixlen = subnetpool.get(prefixlen_attr,
                                   constants.ATTR_NOT_SPECIFIED)
        wildcard = self._sp_helper.wildcard(self.ip_version)

        if prefixlen is constants.ATTR_NOT_SPECIFIED and default_bound:
            prefixlen = default_bound

        if prefixlen is not constants.ATTR_NOT_SPECIFIED:
            prefix_cidr = '/'.join((wildcard,
                                    str(prefixlen)))
            setattr(self, prefix_attr, prefix_cidr)
            setattr(self, prefixlen_attr, prefixlen)
```

### `def _read_attrs(self, subnetpool, keys)`

读取子网池的某些属性

```
    def _read_attrs(self, subnetpool, keys):
        for key in keys:
            setattr(self, key, subnetpool[key])
```

### `def _ip_version_from_cidr(self, cidr)`

从 cidr 中计算 ip 版本

```
    def _ip_version_from_cidr(self, cidr):
        return netaddr.IPNetwork(cidr).version
```

### `def _prefixlen_from_cidr(self, cidr)`

从 cidr 中计算 prefixlen 

```
    def _prefixlen_from_cidr(self, cidr):
        return netaddr.IPNetwork(cidr).prefixlen
```