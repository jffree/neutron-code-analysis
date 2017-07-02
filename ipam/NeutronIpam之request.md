# Neutron Ipam 之 request

*neutron/ipam/request.py*

1. Ipam（ip address management，ip 地址管理）中两种请求：
 1. 一种是从子网池（subnet pool）中为网络（network）分配子网（subnet）的请求
 2. 另一种是从子网（subnet）中为端口（port）分配 ip 地址的请求
2. 根据请求的不同，分为两种处理方式：
 1. 在 `Pool.get_subnet_request_factory` 调用 `SubnetRequestFactory.get_request` 来处理分配子网的请求
 2. 在 `Pool.get_address_request_factory` 调用 `AddressRequestFactory.get_request` 来处理分配地址的请求
3. 对于分配子网的请求来说，根据请求数据的不同又可以分为两类：
 1. 若分配子网的请求数据中包含了 `cidr` 属性，则调用 `SpecificSubnetRequest` 做进一步的处理
 2. 若分配子网的请求数据中不包含 `cidr` 属性，则调用 `AnySubnetRequest` 做进一步的处理
4. 对于分配地址来说，分为四种处理方式
 1. 


## `class SubnetRequestFactory(object)`

### `def get_request(cls, context, subnet, subnetpool)`

根据 subnet 的请求数据中是否包含了 `cidr` 属性，来进行更进一步的处理：

1. 若请求数据中包含了 `cidr` 属性，则调用 `SpecificSubnetRequest` 做进一步的处理
2. 若请求数据中不包含 `cidr` 属性，则调用 `AnySubnetRequest` 做进一步处理

## `class AddressRequestFactory(object)`

 