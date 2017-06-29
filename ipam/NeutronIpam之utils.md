# Neutron Ipam 之 utils 

*neutron/ipam/utils.py*

这个模块实现了 Ipam 常用的方法。

## `def generate_pools(cidr, gateway_ip)`

根据 cidr 和设定的 gateway_ip 生成地址池（利用 `netaddr` 模块实现）。

对于 ipv4，要掐头去尾；
对于 ipv6，要去头；
若 `gateway_ip` 不为空，则要在地址池中去掉网关地址