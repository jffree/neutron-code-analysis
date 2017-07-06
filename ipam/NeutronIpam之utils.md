# Neutron Ipam 之 utils 

*neutron/ipam/utils.py*

这个模块实现了 Ipam 常用的方法。

## `def generate_pools(cidr, gateway_ip)`

根据 cidr 和设定的 gateway_ip 生成以 `netaddr.IPRange` 表示的地址池（利用 `netaddr` 模块实现）。

对于 ipv4，要掐头去尾；
对于 ipv6，要去头；
若 `gateway_ip` 不为空，则要在地址池中去掉网关地址

## `def check_subnet_ip(cidr, ip_address)`

根据该子网的 cidr 检查这个 ip 地址（将要从该子网分配）是否可被分配。

1. 被分配的 Ip 地址不能是网络地址
2. 若 ip 版本为4，则不能分配该子网的广播地址
3. 该 Ip 要在 cidr 范围内

## `def check_gateway_invalid_in_subnet(cidr, gateway)`

对于该子网来说，检查该网关地址是否正确。

1. 网关地址要在子网范围内
2. 网关地址不能为网络地址和广播地址