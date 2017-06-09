# Neutron ML2 之网络调度

`Ml2Plugin` 在初始化时会调用 `_setup_dhcp` 创建一个网络调度对象

```
    def _setup_dhcp(self):
         """Initialize components to support DHCP."""
         self.network_scheduler = importutils.import_object(
             cfg.CONF.network_scheduler_driver
         )
         self.add_periodic_dhcp_agent_status_check()
```

在 */etc/neutron/neutron.conf* 中我们看到默认的调度驱动为：

```
network_scheduler_driver = neutron.scheduler.dhcp_agent_scheduler.WeightScheduler
```