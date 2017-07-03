# Neutron Ipam 之 request

*neutron/ipam/request.py*

## 简介

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

## 测试

```
neutron address-scope-create --shared simple-scope 4  #创建地址范围
neutron subnetpool-create --pool-prefix 10.0.1.0/8 --pool-prefix 10.0.2.0/8 --address-scope simple-scope --min-prefixlen 12 --max-prefixlen 20 --default-prefixlen 16 --shared --description 'This is a test simple subnet pool.' simple-subnetpool #创建子网池
neutron net-create --router:external --provider:physical_network simple --provider:network_type flat --shared --description 'This is a simple network' simple-net #创建网络
neutron subnet-create --name simple-subnet --subnetpool simple-subnetpool --prefixlen 14 simple-net #创建子网
```

## 如何增加一个 physical network？

在创建网络的时候，我们会看到这么几个参数：`--provider:network_type`、`--provider:physical_network`、`--provider:segmentation_id`，这几个是创建 provider 网络的。

关于 provider 网络与 tenant 网络的区别请参考：[ Neutron 中的 Provider Network 和 Tenant Network](http://blog.csdn.net/zhaoeryi/article/details/38494929)

## 参考

[OpenStack网络指南（12）BGP动态路由](http://www.2cto.com/net/201612/581717.html)
[ Neutron 中的 Provider Network 和 Tenant Network ](http://blog.csdn.net/zhaoeryi/article/details/38494929)


## `class SubnetRequestFactory(object)`

### `def get_request(cls, context, subnet, subnetpool)`

## `class AddressRequestFactory(object)`

### `def get_request(cls, context, port, ip_dict)`
 
## `class SubnetRequest(object)`

```
@six.add_metaclass(abc.ABCMeta)
class SubnetRequest(object)
```

抽象基类，


























