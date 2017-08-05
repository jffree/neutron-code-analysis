# Neutron L2 Ageny L2_pop 与 arp_responser

* 环境说明：
 1. l2 agent 采用 `neutron-openvswitch-agent`
 2. 网络类型为 `vxlan` 

## L2 Population 的功能

### 开启 l2 pop

```
vim /etc/neutron/ml2_conf.ini:

[ml2]
mechanism_drivers = ..., l2population, ...

[agent]
l2_population = True
```

### 启动 l2 pop 之后，neutron-server 做了什么事情？

1. 加载 l2population 的 mechanism driver：`L2populationMechanismDriver`（*neutron/plugins/ml2/l2pop/mech_driver.py*）
2. l2pop mech driver 会创建一个 RPC Client（`L2populationAgentNotifyAPI`），用于将 Port 资源的创建、删除、更新操作发送到 RPC Server（`OVSNeutronAgent`）

### 开启 l2 pop 之后，l2 agent 做了什么事情呢？

1. 忽略 `tunnel_update` 和 `tunnel_sync` 中建立 tunnel port 的操作（`OVSNeutronAgent._setup_tunnel_port`）
2. 启动监听来自 `l2pop mech driver` 发送的 RPC 消息（`OVSNeutronAgent.setup_rpc`），并处理相关的请求

* 那么我们有下面两个疑问
 1. tunnel port 创建的过程中都做了什么工作（未开启 l2 pop 是 l2 agent 都做了什么）？
  1. 创建一个与其他 l2 agent 交互的端口（也就是 vxlan 的 vtep）
  2. 在 br-tun 上创建一个如下的流表：`cookie=0x8ca031df7a84a666, duration=261777.055s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,in_port=2 actions=resubmit(,4)`（作用：将从刚才创建的 tunnel port 进入的数据包转发到 table 4 进行处理）
  3. 在 br-tun 上创建一个如下的流表：`cookie=0x8ca031df7a84a666, duration=168660.093s, table=22, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,dl_vlan=1 actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:2,output:3`（作用：将离开当前 agent 的数据包转发到其他所有的 agent）
 2. 开启 l2 pop 后（l2 pop 会接管 tunnel port），l2 pop 做了其他的什么工作？
  * 在 br-tun 上额外创建了如下的流表：`cookie=0x8ca031df7a84a666, duration=262471.237s, table=20, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_vlan=1,dl_dst=fa:16:3e:51:3b:f7 actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:3`（作用：对于指定目的的访问之发送到特定的 agent，而不再发送到所有的 agent） 

## ARP Responser 的功能

* 开启 ARP Responser 功能：

```
vim /etc/neutron/ml2_conf.ini:

[ml2]
mechanism_drivers = ..., l2population, ...

[agent]
l2_population = True
arp_responder = True
```

*ARP Responser 是 L2 Population 功能的一种延伸，就是必须在开启 l2pop 的前提下才能开启 arp responser。*

* 那么开启 ARP Responer 后，l2 pop 又做了什么工作呢？
 * 在 br-tun 上额外创建了如下流表：`cookie=0x8ca031df7a84a666, duration=263354.597s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=1,arp_tpa=192.168.100.2 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163e513bf7->NXM_NX_ARP_SHA[],load:0xc0a86402->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:51:3b:f7,IN_PORT`（作用：当有询问 192.168.100.2 的 mac 地址的 arp 请求，从 br-int 发过来时，这条流表会直接修改数据包将 192.168.100.2 的 mac 地址写入，并从入口直接返回，做为 ARP response）

## 总结

neutron-server 中维护着所有 port 的详细数据，所以当云内的资源互相访问时，可以做到不发送广播，而直接获取想要的数据，l2 pop 就是实现这个功能。

## 参考

[ML2 – Address Population](https://assafmuller.com/2014/02/23/ml2-address-population/)
[OVS ARP Responder – Theory and Practice](https://assafmuller.com/2014/05/21/ovs-arp-responder-theory-and-practice/)