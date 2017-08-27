# Neutron Dns Extension

*neutron/db/dns_db.py*

## extensions

*neutron/extensions/dns.py*

## 数据库

```
class NetworkDNSDomain(model_base.BASEV2)

class FloatingIPDNS(model_base.BASEV2)

class PortDNS(model_base.BASEV2)
```

```
class DNSActionsData(object):

    def __init__(self, current_dns_name=None, current_dns_domain=None,
                 previous_dns_name=None, previous_dns_domain=None):
        self.current_dns_name = current_dns_name
        self.current_dns_domain = current_dns_domain
        self.previous_dns_name = previous_dns_name
        self.previous_dns_domain = previous_dns_domain
```

## `class DNSDbMixin(object)`

*dns extension WSGI 实现*

### `def dns_driver(self)`

属性方法，用来加载 dns driver

*只有在配置中指明 `external_dns_driver` 选项，才会加载 dns driver*

调用 `driver.ExternalDNSService.get_instance` 实现驱动的加载

## `class ExternalDNSService(object)`

*dns driver 的抽象基类*

### `def get_instance(cls)`

1. 通过调用 `manager.NeutronManager.load_class_for_provider` 实现 dns driver 的加载
2. 实例化 dns driver

在 *steup.cfg* 中，可以看到 dns driver 的可用驱动如下：

```
neutron.services.external_dns_drivers =
    designate = neutron.services.externaldns.drivers.designate.driver:Designate
```

## `class Designate(driver.ExternalDNSService)`

dns driver

```
    def __init__(self):
        ipv4_ptr_zone_size = CONF.designate.ipv4_ptr_zone_prefix_size
        ipv6_ptr_zone_size = CONF.designate.ipv6_ptr_zone_prefix_size

        if (ipv4_ptr_zone_size < IPV4_PTR_ZONE_PREFIX_MIN_SIZE or
            ipv4_ptr_zone_size > IPV4_PTR_ZONE_PREFIX_MAX_SIZE or
            (ipv4_ptr_zone_size % 8) != 0):
            raise dns.InvalidPTRZoneConfiguration(
                parameter='ipv4_ptr_zone_size', number='8',
                maximum=str(IPV4_PTR_ZONE_PREFIX_MAX_SIZE),
                minimum=str(IPV4_PTR_ZONE_PREFIX_MIN_SIZE))

        if (ipv6_ptr_zone_size < IPV6_PTR_ZONE_PREFIX_MIN_SIZE or
            ipv6_ptr_zone_size > IPV6_PTR_ZONE_PREFIX_MAX_SIZE or
            (ipv6_ptr_zone_size % 4) != 0):
            raise dns.InvalidPTRZoneConfiguration(
                parameter='ipv6_ptr_zone_size', number='4',
                maximum=str(IPV6_PTR_ZONE_PREFIX_MAX_SIZE),
                minimum=str(IPV6_PTR_ZONE_PREFIX_MIN_SIZE))
```

### `def create_record_set(self, context, dns_domain, dns_name, records)`



### `def delete_record_set(self, context, dns_domain, dns_name, records)`

