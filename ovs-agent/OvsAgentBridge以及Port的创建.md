# Ovs agent br 以及 port 的创建

1. `setup_integration_br` 
 1. 创建 br-int
2. `setup_physical_bridges` 
 1. 创建 br-ex
 2. 创建 int-br-ex（br-int）
 3. 创建 phy-br-ex（br-ex） 
3. `setup_tunnel_br`
 1. 创建 br-tun
 2. 创建 patch-tun（br-int）
 3. 创建 patch-int（br-tun）