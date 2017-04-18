# API Extensions

API扩展是向Neutron项目引入新功能的标准方法，它允许插件确定是否希望支持该功能。

## Examples

演示如何编写API扩展的最简单方法是通过研究现有的API扩展并解释不同的层。

[Guided Tour: The Neutron Security Group API](https://docs.openstack.org/developer/neutron/devref/security_group_api.html)

## 具有标准属性的资源扩展

从`HasStandardAttributes DB`类继承的资源可以自动为标准属性（例如时间戳，修订版本号等）编写的扩展名通过在其模型上定义`api_collections`来扩展其资源。这些由标准attr资源的扩展用于生成扩展资源映射。

必须在标准属性集合中添加新的资源，并附加一个新的扩展名，以确保通过API可以发现。 如果它是一个全新的资源，那么描述该资源的扩展就足够了。 如果它是在上一个循环中发布的现有资源，其中第一次添加了标准属性，则需要添加一个虚拟扩展，指示资源现在具有标准属性。 这样可以确保API调用者始终可以发现属性是否可用。

例如，如果将Flavors迁移到包含标准属性，则需要一个新的“flavor-standardattr”扩展名。然后作为一个API调用者，我会知道，通过检查'flavor-standardattr'和'timestamps'，falvor将具有时间戳。

当前API资源由标准的attr扩展扩展：

* subnets: neutron.db.models_v2.Subnet
* trunks: neutron.services.trunk.models.Trunk
* routers: neutron.db.l3_db.Router
* segments: neutron.db.segments_db.NetworkSegment
* security_group_rules: neutron.db.models.securitygroup.SecurityGroupRule
* networks: neutron.db.models_v2.Network
* policies: neutron.db.qos.models.QosPolicy
* subnetpools: neutron.db.models_v2.SubnetPool
* ports: neutron.db.models_v2.Port
* security_groups: neutron.db.models.securitygroup.SecurityGroup
* floatingips: neutron.db.l3_db.FloatingIP