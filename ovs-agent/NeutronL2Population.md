# Neutron L2 population

## L2 population 的开启

```
[ml2]
...
mechanism_drivers = openvswitch,linuxbridge,l2population

[agent]
...
l2_population = True
```

重启 neutron-server 服务，重启 neutron-agent 服务

## l2 population 的 RPC 消息流通

Client：`L2populationAgentNotifyAPI`
Server：`OVSNeutronAgent`

1. neutron-server 告诉 mech l2 driver 有 port 的创建、删除、更新操作产生时，mech l2 driver 会调用 RPC Client 来通知 Server 端有新的 fdb 表需要创建
2. RPC Server 端收到 RPC 消息后，会根据消息的种类进行不同的操作。

## l2 pop RPC 消息的种类

1. 增加 fdb 表，这又分为两种
 1. 第一种是一个新的 agent 启用（其余的 agent 需要创建用来访问该 agent 的 vtep）
 2. 第二种是一个新 port 的创建
2. 删除 fdb 表，这也分为两种
 1. 第一种是一个旧的 agent 弃用（其余的 agent 需要删除用来访问该 agent 的 vtep）
 2. 第二种是一个旧 port 的删除
3. 修改 fdb 表（当一个 port 的 ip 或者 mac 地址发生变化时） 

## l2 pop RPC Server 收到消息后的处理方式

* 对于 vtep 的创建需要在 flood 表 22 增加一条 flood 消息的处理

```
[root@node2 ~]# ovs-ofctl dump-flows br-tun table=22
NXST_FLOW reply (xid=0x4):
 cookie=0x8ca031df7a84a666, duration=47839.070s, table=22, n_packets=0, n_bytes=0, idle_age=65534, priority=1,dl_vlan=1 actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:2,output:3
```

* 对于普通 port 的创建，需要有两步操作：第一，创建该 port 的 arp reposer 流表；第二，创建该 port 的单播流表

```
[root@node1 ~]# ovs-ofctl dump-flows br-tun table=21
NXST_FLOW reply (xid=0x4):
 cookie=0x8d92abaa691e5b6d, duration=141302.724s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=3,arp_tpa=192.168.100.5 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163e5c9e2d->NXM_NX_ARP_SHA[],load:0xc0a86405->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:5c:9e:2d,IN_PORT
```

```
[root@node1 ~]# ovs-ofctl dump-flows br-tun table=20
NXST_FLOW reply (xid=0x4):
 cookie=0x8d92abaa691e5b6d, duration=141319.556s, table=20, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_vlan=3,dl_dst=fa:16:3e:5c:9e:2d actions=strip_vlan,load:0x5d->NXM_NX_TUN_ID[],output:3
```

* 删除 port 则会引发删除 fdb flow entity 的操作（与上面的动作相反）。

## 参考

[ 创建 VXLAN - 每天5分钟玩转 OpenStack（111） ](http://blog.csdn.net/CloudMan6/article/details/53115993)
[ 部署 instance 到 VXLAN - 每天5分钟玩转 OpenStack（112） ](http://blog.csdn.net/CloudMan6/article/details/53149952)
[ L2 Population 原理 - 每天5分钟玩转 OpenStack（113） ](http://blog.csdn.net/cloudman6/article/details/53167522)
[配置 L2 Population - 每天5分钟玩转 OpenStack（114） ](http://blog.csdn.net/CloudMan6/article/details/53195077)