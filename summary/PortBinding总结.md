# port binding 总结

1. Port Bingding 是在 Neutron Server 端完成的，主要的是在数据库中记录 Port 与 Host 的绑定关系。
2. 涉及到的数据库有：`PortBinding`、`PortBindingLevel`、`DistributedPortBinding`
3. 涉及到的模块：
 1. *neutron/plugins/ml2/plugin.py* 创建 Port 的时候，是 Port Binding 的开始；创建 Port 完成，也是 Port Binding 的结束。
 2. *neutron/plugins/ml2/managers.py* `MechanismManager` 会根据实现机制的不同（ovs、linuxbridge 等）来进行调用
 3. *neutron/plugins/ml2/driver_context.py* 包含了当下用到的 network、subnet、port 的相关的详细信息
 4. *neutron/plugins/ml2/drivers/** 下的不同实现机制（ovs、linuxbridge）

## 疑问

[ML2: Hierarchical Port Binding](http://specs.openstack.org/openstack/neutron-specs/specs/kilo/ml2-hierarchical-port-binding.html)

这个是什么意思？











