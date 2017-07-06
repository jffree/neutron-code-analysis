Ipam：Ip 地址管理

## 总结

* ipam 实现的是 IP 地址的管理：
 1. 如何从子网池中分配和回收子网
 2. 如何从子网中分配和回收单个的 Ip 地址

* ipam 不负责子网的其他属性的管理：
 1. 不负责管理 service_types 属性
 2. 不负责管理 segment_id 属性
 3. 不负责管理 host_routes 属性
 4. 不负责管理 service_types 属性

## ipam 之数据库描述：

*类似于 Neutron object 用一个类来实现对一条数据库记录的描述。*

1. `NeutronDbSubnet` 来描述一个 subnet 的数据库记录，同时实现了从该子网中分配 Ip 地址
2. `SubnetPoolReader` 实例用来描述一条 `subnetpool` 的数据库记录

## 子网的分配

`NeutronDbPool` 实现了从子网池中分配子网

## ipam 之 request

1. Ipam（ip address management，ip 地址管理）中两种请求：
 1. 一种是从子网池（subnet pool）中为网络（network）分配子网（subnet）的请求
 2. 另一种是从子网（subnet）中为端口（port）分配 ip 地址的请求
2. 根据请求的不同，分为两种处理方式：
 1. 在 `Pool.get_subnet_request_factory` 调用 `SubnetRequestFactory.get_request` 来处理分配子网的请求
 2. 在 `Pool.get_address_request_factory` 调用 `AddressRequestFactory.get_request` 来处理分配地址的请求
3. 对于分配子网的请求来说，根据请求数据的不同又可以分为两类：
 1. 若分配子网的请求数据中包含了 `cidr` 属性，则调用 `SpecificSubnetRequest` 做进一步的处理
 2. 若分配子网的请求数据中不包含 `cidr` 属性，则调用 `AnySubnetRequest` 做进一步的处理
4. 对于分配 ip 地址来说，分为四种处理方式
 1. 若分配 ip 地址的请求数据中包含了 `ip_address` 属性，则调用 `SpecificAddressRequest` 做进一步的处理
 2. 若分配 ip 地址的请求数据中包含了 `eui64_address` 属性，则调用 `AutomaticAddressRequest` 做进一步的处理
 3. 若分配 ip 地址的请求数据中包含了 `device_owner` 属性，则调用 `PreferNextAddressRequest` 做进一步的处理
 4. 若分配 ip 地址的请求数据中不包含以上三种属性，则调用 `AnyAddressRequest` 做进一步的处理

## ipam 之 子网管理

`IpamSubnetManager`

* subnet 地址分配的管理类，只负责与 ipam 相关的数据库交互

## subnetpool 的 quota

subnetpool 的 quota 是根据用户可用的 ip 地址的个数来限制的。

限制字段在 `SubnetPool` 数据库的 `default_quota` 字段中。

从这里看，同一个地址池，真多所用的可访问它的用户的 quota 配额是一样的。