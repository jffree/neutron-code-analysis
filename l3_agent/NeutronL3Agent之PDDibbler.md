# Neutron l3 agent 之 PDDibbler

## `class PDDriverBase(object)`

抽象基类，定义了框架

*neutron/agent/linux/pd_driver.py*

```
    def __init__(self, router_id, subnet_id, ri_ifname):
        self.router_id = router_id
        self.subnet_id = subnet_id
        self.ri_ifname = ri_ifname
```


## `class PDDibbler(pd_driver.PDDriverBase)`

*neutron/agent/linux/dibbler.py*

```
    def __init__(self, router_id, subnet_id, ri_ifname):
        super(PDDibbler, self).__init__(router_id, subnet_id, ri_ifname)
        self.requestor_id = "%s:%s:%s" % (self.router_id,
                                          self.subnet_id,
                                          self.ri_ifname)
        self.dibbler_client_working_area = "%s/%s" % (cfg.CONF.pd_confs,
                                                      self.requestor_id)
        self.prefix_path = "%s/prefix" % self.dibbler_client_working_area
        self.pid_path = "%s/client.pid" % self.dibbler_client_working_area
        self.converted_subnet_id = self.subnet_id.replace('-', '')
```

### `def get_sync_data()`

*本配置中在 neutron 数据目录 /opt/stack/data/neutron/ 下没有发现 pd 的任何数据文件。所以这个方法我们以后再将*
























