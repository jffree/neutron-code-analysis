## 下一步计划

1. neutron l3 agent legacy 模式分析
2. neutron l3 agent dvr 模式分析
3. dvr 与 dvr_snat 的区别
4. l3 agent ha
5. l3 agent floaying ip

[Multinode DVR Devstack](https://assafmuller.com/2015/04/06/multinode-dvr-devstack/)
[Distributed Virtual Routing – Overview and East/West Routing](https://assafmuller.com/2015/04/15/distributed-virtual-routing-overview-and-eastwest-routing/)
[Distributed Virtual Routing – SNAT](https://assafmuller.com/2015/04/15/distributed-virtual-routing-snat/)
[Distributed Virtual Routing – Floating IPs](https://assafmuller.com/2015/04/15/distributed-virtual-routing-floating-ips/)
[理解 OpenStack 高可用（HA）（3）：Neutron 分布式虚拟路由（Neutron Distributed Virtual Routing）](http://www.cnblogs.com/sammyliu/p/4713562.html)
[OpenStack Neutron 之 L3 HA](https://www.ibm.com/developerworks/cn/cloud/library/1506_xiaohh_openstackl3/)
[理解 OpenStack 高可用（HA）（2）：Neutron L3 Agent HA 之 虚拟路由冗余协议（VRRP）](http://www.cnblogs.com/sammyliu/p/4692081.html)
[虚拟路由器冗余协议【原理篇】VRRP详解 ](http://zhaoyuqiang.blog.51cto.com/6328846/1166840/)
[Layer 3 High Availability](https://assafmuller.com/2014/08/16/layer-3-high-availability/)

## 学习步骤

### 非 dvr、非 l2pop

#### 网络节点：

* l2 agent

* l3 agent

#### 计算节点：

* l2 agent

* l3 agent（无）

### l2pop and arp responser

#### 网络节点：

* l2 agent

```
vim ml2_conf.ini:
```

> [ml2]
mechanism_drivers = ..., l2population, ...

> [agent]
l2_population = True
arp_responder = True

* l3 agent

```
vim l3_agent.ini
```

> agent_mode = legacy


* 参考

[ML2 – Address Population](https://assafmuller.com/2014/02/23/ml2-address-population/)


#### 计算节点：

* l2 agent

```
vim ml2_conf.ini:
```

> [ml2]
mechanism_drivers = ..., l2population, ...

> [agent]
l2_population = True
arp_responder = True


* l3 agent（无）


### dvr

#### 网络节点：

* neutron-server

```
vim neutron.conf
```

> router_distributed = True 


* l2 agent

```
vim ml2_conf.ini:
```

> [agent]
enable_distributed_routing = True

* l3 agent

```
vim l3_agent.ini
```

> agent_mode = dvr_snat

#### 计算节点：

* l2 agent

```
vim ml2_conf.ini:
```

> [agent]
enable_distributed_routing = True


* l3 agent

```
vim l3_agent.ini
```

> agent_mode = dvr

