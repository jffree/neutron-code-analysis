# 使用 OVS 创建一个 provider network

**provider network 建立在物理网络之上**

[Scenario: Provider networks with Open vSwitch](https://docs.openstack.org/liberty/networking-guide/scenario-provider-ovs.html)

## 情景

管理网络：10.0.0.0/24。
provider 网络使用 192.0.2.0/24，198.51.100.0/24 和 203.0.113.0/24。
控制节点：两个网口：一个用作管理网络、一个用作 provider 网络
结算节点：两个网口：一个用作管理网络、一个用作 provider 网络
用作 provider 网络的端口需要连接外部的物理路由器或者交换机，进而连接外部网络（通常为 internet）。

![硬件层](https://docs.openstack.org/liberty/networking-guide/_images/scenario-provider-hw.png)
![网络层](https://docs.openstack.org/liberty/networking-guide/_images/scenario-provider-networks.png)
![服务层](https://docs.openstack.org/liberty/networking-guide/_images/scenario-provider-ovs-services.png)
![通用架构](https://docs.openstack.org/liberty/networking-guide/_images/scenario-provider-general.png)
![控制节点网络构成](https://docs.openstack.org/liberty/networking-guide/_images/scenario-provider-ovs-controller2.png) 
![计算节点网络构成](https://docs.openstack.org/liberty/networking-guide/_images/scenario-provider-ovs-compute2.png)