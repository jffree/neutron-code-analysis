# Neutron L3 Agent 之 LinkLocalAddressPair

*neutron/agent/l3/link_local_allocator.py*

## `class LinkLocalAddressPair(netaddr.IPNetwork)`

```
class LinkLocalAddressPair(netaddr.IPNetwork):
    def __init__(self, addr):
        super(LinkLocalAddressPair, self).__init__(addr)

    def get_pair(self):
        """Builds an address pair from the first and last addresses. """
        # TODO(kevinbenton): the callers of this seem only interested in an IP,
        # so we should just return two IPAddresses.
        return (netaddr.IPNetwork("%s/%s" % (self.network, self.prefixlen)),
                netaddr.IPNetwork("%s/%s" % (self[-1], self.prefixlen)))
```

`get_pair` 用于返回该 network 的第一个和最后一个 Ip 地址对


## `class LinkLocalAllocator(ItemAllocator)`

```
class LinkLocalAllocator(ItemAllocator):
    """Manages allocation of link local IP addresses.

    These link local addresses are used for routing inside the fip namespaces.
    The associations need to persist across agent restarts to maintain
    consistency.  Without this, there is disruption in network connectivity
    as the agent rewires the connections with the new IP address associations.

    Persisting these in the database is unnecessary and would degrade
    performance.
    """
    def __init__(self, data_store_path, subnet):
        """Create the necessary pool and item allocator
            using ',' as the delimiter and LinkLocalAllocator as the
            class type
        """
        subnet = netaddr.IPNetwork(subnet)
        pool = set(LinkLocalAddressPair(s) for s in subnet.subnet(31))
        super(LinkLocalAllocator, self).__init__(data_store_path,
                                                 LinkLocalAddressPair,
                                                 pool)
```

在 subnet 的基础上构造网络前缀为 31 的全部子网

可用如下方法查看：

```
list(netaddr.IPNetwork('169.254.64.0/18').subnet(31))
```