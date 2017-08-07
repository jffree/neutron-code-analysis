# Neutron l3 agent 之 MetadataDriver

*neutron/agent/metadata/driver.py*

## `class MetadataDriver(object)`

```
    monitors = {}

    def __init__(self, l3_agent):
        self.metadata_port = l3_agent.conf.metadata_port
        self.metadata_access_mark = l3_agent.conf.metadata_access_mark
        registry.subscribe(
            after_router_added, resources.ROUTER, events.AFTER_CREATE)
        registry.subscribe(
            after_router_updated, resources.ROUTER, events.AFTER_UPDATE)
        registry.subscribe(
            before_router_removed, resources.ROUTER, events.BEFORE_DELETE)
```

* `metadata_port` 默认为 9697
* `metadata_access_mark` 默认为 0x1（*Iptables mangle mark used to mark metadata valid requests.*）
* 在系统回调中的感兴趣资源及其事件
 1. resource : `ROUTER` ;  event : `AFTER_CREATE` ; callback : `after_router_added`
 2. resource : `ROUTER` ;  event : `AFTER_UPDATE` ; callback : `after_router_updated`
 3. resource : `ROUTER` ;  event : `BEFORE_DELETE` ; callback : `before_router_removed`


















