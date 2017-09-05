# Neutron L3 Agent 之 LegacyRouter

*neutron/agent/l3/legacy_router.py*

## `class LegacyRouter(router.RouterInfo)`

### `def add_floating_ip(self, fip, interface_name, device)`

```
    def add_floating_ip(self, fip, interface_name, device):
        if not self._add_fip_addr_to_device(fip, device):
            return lib_constants.FLOATINGIP_STATUS_ERROR

        # As GARP is processed in a distinct thread the call below
        # won't raise an exception to be handled.
        ip_lib.send_ip_addr_adv_notif(self.ns_name,
                                      interface_name,
                                      fip['floating_ip_address'],
                                      self.agent_conf)
        return lib_constants.FLOATINGIP_STATUS_ACTIVE
```

调用 `_add_fip_addr_to_device` 来将 floating ip 添加到 device 上
若失败，则返回 `FLOATINGIP_STATUS_ERROR`
若成功，则调用 `send_ip_addr_adv_notif` 发送 arp 通知