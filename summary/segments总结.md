## neutron-server TypeManager 总结

**segment 是和 network 成对出现的，也就是每个 network 都会有一个对应的 segment。**

*TypeManager 实现了针对不同**网络**的 segment 的创建和管理，这里只有在 neutron-server 上的数据库操作，并不会与其他的 agent 产生协作。*

* TypeManager 实现模块：*neutron/plugins/ml2/managers.py*

* **local network**
  1. 数据库：无
  2. 实现模块：*neutron/plugins/ml2/drivers/type_local.py*
  
* **flat network**
  1. 数据库：`FlatAllocation`
  2. 实现模块：*neutron/plugins/ml2/drivers/type_flat.py*

* **vlan network**
  1. 数据库：`VlanAllocation`
  2. 实现模块：*neutron/plugins/ml2/drivers/helpers.py*、*neutron/plugins/ml2/drivers/type_vlan.py*
  
* **vxlan network**
  1. 数据库：`VxlanAllocation`、`VxlanEndpoints`
  2. 实现模块：*neutron/plugins/ml2/drivers/helpers.py*、*neutron/plugins/ml2/drivers/type_tunnel.py*、*neutron/plugins/ml2/drivers/type_vxlan.py*

* **gre network**
  1. 数据库：`GreAllocation`、`GreEndpoints`
  2. 实现模块：*neutron/plugins/ml2/drivers/helpers.py*、*neutron/plugins/ml2/drivers/type_tunnel.py*、*neutron/plugins/ml2/drivers/type_gre.py*

* **geneve**
  1. 数据库：`GeneveAllocation`、`GeneveEndpoints`
  2. 实现模块：*neutron/plugins/ml2/drivers/helpers.py*、*neutron/plugins/ml2/drivers/type_tunnel.py*、*neutron/plugins/ml2/drivers/type_geneve.py*
  
1. 这些所有的数据库记录都会再次增加到 `NetworkSegment` 这个数据库中，以方便其他的模块使用 segment
2. neutron 支持的网络类型是通过配置文件中的 `type_drivers` 进行设定的，默认是所有的网络类型都支持：`local,flat,vlan,gre,vxlan,geneve`
3. tenant network 创建时是不能指定网络类型的，只能是根据配置文件中 `tenant_network_types` 来确定的。
4. 未指定 `provider-*` 或者 `segments` 属性的 external network，其网络类型是根据配置文件中的 `external_network_type` 确定的 
5. 创建 provider-* 和 segments 属性只能指定一个（segments 是包含了多个 provider-* 属性）
6. 提供了 `provider-*` 或者 `segments` 属性后，就可以明确的设定该 network 的 segment 属性：`provider:network_type`、`provider:physical_network`、`provider:segmentation_id`