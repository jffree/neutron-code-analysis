# 开启 L2 POP 后 ARP 请求的处理

## 系统结构图如下

* 网络节点结构图

![]()

* 计算节点一结构图

![]()

* 计算节点二结构图

![]()

## ARP 请求的处理过程

*我们从 vm1（计算节点一）来 ping vm2（计算节点二）。（我们不讲 Ping 的过程，我们将 APR 的相应过程）*

* vm1:
 * ip : 192.168.100.5, 172.16.100.250
 * mac : fa:16:3e:5c:9e:2d

* vm2
 * ip : 192.168.200.8, 172.16.100.243
 * mac : fa:16:3e:71:5a:c6

* 从 vm1 发出的网络包，既是从 tap9c2639b3-02 发出的包，其会经过： **tap9c2639b3-02 --> qbr9c2639b3-02 --> qvb9c2639b3-02 --> qvo9c2639b3-02** 这样子的路径来到达网桥 **br-int**（其中 **qvo9c2639b3-02** 在 **br-int** 中的 **ofport** 为 3 ）。 

* 我们看 br-int 的 table 0 的规则：

```
[root@node2 ~]# ovs-ofctl dump-flows br-int table=0
NXST_FLOW reply (xid=0x4):
 cookie=0xb637cdfd05911130, duration=176395.278s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=10,icmp6,in_port=3,icmp_type=136 actions=resubmit(,24)
 cookie=0xb637cdfd05911130, duration=176395.274s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=10,arp,in_port=3 actions=resubmit(,24)
 cookie=0xb637cdfd05911130, duration=176403.669s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=1 actions=drop
 cookie=0xb637cdfd05911130, duration=176395.284s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=9,in_port=3 actions=resubmit(,25)
 cookie=0xb637cdfd05911130, duration=176403.631s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=4,in_port=1,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,2)
 cookie=0xb637cdfd05911130, duration=176403.626s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=7,dl_src=fa:16:3f:24:77:e3 actions=resubmit(,1)
 cookie=0xb637cdfd05911130, duration=176403.621s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=4,in_port=1,dl_src=fa:16:3f:cb:84:46 actions=resubmit(,2)
 cookie=0xb637cdfd05911130, duration=176403.614s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=7,dl_src=fa:16:3f:cb:84:46 actions=resubmit(,1)
 cookie=0xb637cdfd05911130, duration=176399.864s, table=0, n_packets=946, n_bytes=90471, idle_age=11969, hard_age=65534, priority=3,in_port=1,vlan_tci=0x0000/0x1fff actions=mod_vlan_vid:3,NORMAL
 cookie=0xb637cdfd05911130, duration=176403.672s, table=0, n_packets=21, n_bytes=882, idle_age=12310, hard_age=65534, priority=1 actions=NORMAL
```

*可以看到，从 ofport=3 进来的 arp 请求会被转发到 table 24 中继续处理*

* br-int table 24 的规则为：

```
[root@node2 ~]# ovs-ofctl dump-flows br-int table=24
NXST_FLOW reply (xid=0x4):
 cookie=0xb637cdfd05911130, duration=176550.999s, table=24, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,icmp6,in_port=3,icmp_type=136,nd_target=fe80::f816:3eff:fe5c:9e2d actions=NORMAL
 cookie=0xb637cdfd05911130, duration=176550.994s, table=24, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,arp,in_port=3,arp_spa=192.168.100.5 actions=resubmit(,25)
```

*将来自 192.168.100.5 （vm1）的 arp 请求转发到表 25 继续处理*

* br-int table 25 的规则为：

```
[root@node2 ~]# ovs-ofctl dump-flows br-int table=25
NXST_FLOW reply (xid=0x4):
 cookie=0xb637cdfd05911130, duration=177359.296s, table=25, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=3,dl_src=fa:16:3e:5c:9e:2d actions=NORMAL
```

*对 in_port 为 3，mac 源为 fa:16:3e:5c:9e:2d 的数据流做正常的转发处理。*

*既然是正常的转发，那么就会转发到 *qr-0b1f0748-fd*、*int-br-ex*、*patch-tun*，这三个端口，其中 `qr-0b1f0748-fd` 是网关端口，不会相应 arp 请求的。*

* arp 请发发送至 *int-br-ex* 端口口会通过 *phy-br-ex* 进入 br-ex 网桥，我们看一下这里面的规则：

```
[root@node2 ~]# ovs-ofctl dump-flows br-ex table=0
NXST_FLOW reply (xid=0x4):
 cookie=0xa02e63c944a0b07b, duration=177713.598s, table=0, n_packets=21, n_bytes=882, idle_age=13623, hard_age=65534, priority=4,in_port=1,dl_vlan=3 actions=strip_vlan,NORMAL
 cookie=0xa02e63c944a0b07b, duration=177717.391s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=1 actions=resubmit(,1)
 cookie=0xa02e63c944a0b07b, duration=177761.155s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=0 actions=NORMAL
 cookie=0xa02e63c944a0b07b, duration=177717.389s, table=0, n_packets=946, n_bytes=90471, idle_age=13283, hard_age=65534, priority=1 actions=resubmit(,3)
```

*对于 inport=1 dl_vlan 不等于 3 的会转发到 table 1 继续处理*

* br-ex table 1 规则

```
[root@node2 ~]# ovs-ofctl dump-flows br-ex table=1
NXST_FLOW reply (xid=0x4):
 cookie=0xa02e63c944a0b07b, duration=177848.757s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=0 actions=resubmit(,2)
```

*到达 table 1 中的数据流会被直接转发到 table 2 中继续处理*

```
[root@node2 ~]# ovs-ofctl dump-flows br-ex table=2
NXST_FLOW reply (xid=0x4):
 cookie=0xa02e63c944a0b07b, duration=177884.665s, table=2, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,in_port=1 actions=drop
```

*到达 table 2 的数据流会被直接丢弃。那么，我们看一下 br-tun 是怎么处理这个 arp 请求的*

* arp 请发发送至 *patch-tun* 端口口会通过 *patch-int* 进入 br-tun 网桥，我们看一下这里面的规则：

```
[root@node2 ~]# ovs-ofctl dump-flows br-tun table=0
NXST_FLOW reply (xid=0x4):
 cookie=0x8ca031df7a84a666, duration=178011.252s, table=0, n_packets=967, n_bytes=91353, idle_age=13577, hard_age=65534, priority=1,in_port=1 actions=resubmit(,1)
 cookie=0x8ca031df7a84a666, duration=178006.276s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,in_port=2 actions=resubmit(,4)
 cookie=0x8ca031df7a84a666, duration=178006.269s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,in_port=3 actions=resubmit(,4)
 cookie=0x8ca031df7a84a666, duration=178011.290s, table=0, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=0 actions=drop
```

*从 ofport=1 端口进来的数据流会被转发到 table 1 中继续处理。*

* br-tun table 1 规则：

```
[root@node2 ~]# ovs-ofctl dump-flows br-tun table=1
NXST_FLOW reply (xid=0x4):
 cookie=0x8ca031df7a84a666, duration=178064.044s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=3,arp,dl_vlan=1,arp_tpa=192.168.100.1 actions=drop
 cookie=0x8ca031df7a84a666, duration=178063.953s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=3,arp,dl_vlan=2,arp_tpa=192.168.200.1 actions=drop
 cookie=0x8ca031df7a84a666, duration=178064.041s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_vlan=1,dl_dst=fa:16:3e:e0:e5:95 actions=drop
 cookie=0x8ca031df7a84a666, duration=178063.951s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=2,dl_vlan=2,dl_dst=fa:16:3e:dd:73:40 actions=drop
 cookie=0x8ca031df7a84a666, duration=178064.037s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,dl_vlan=1,dl_src=fa:16:3e:e0:e5:95 actions=mod_dl_src:fa:16:3f:4d:40:29,resubmit(,2)
 cookie=0x8ca031df7a84a666, duration=178063.949s, table=1, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,dl_vlan=2,dl_src=fa:16:3e:dd:73:40 actions=mod_dl_src:fa:16:3f:4d:40:29,resubmit(,2)
 cookie=0x8ca031df7a84a666, duration=178072.038s, table=1, n_packets=967, n_bytes=91353, idle_age=13638, hard_age=65534, priority=0 actions=resubmit(,2)
```

*这里可以看到所有访问网关的数据都会被 drop 掉。其他的数据则会转发到 table 2 中继续处理*

* br-tun table 2 的规则

```
[root@node2 ~]# ovs-ofctl dump-flows br-tun table=2
NXST_FLOW reply (xid=0x4):
 cookie=0x8ca031df7a84a666, duration=178807.170s, table=2, n_packets=32, n_bytes=1542, idle_age=14408, hard_age=65534, priority=1,arp,dl_dst=ff:ff:ff:ff:ff:ff actions=resubmit(,21)
 cookie=0x8ca031df7a84a666, duration=178807.167s, table=2, n_packets=661, n_bytes=69781, idle_age=14373, hard_age=65534, priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)
 cookie=0x8ca031df7a84a666, duration=178807.165s, table=2, n_packets=274, n_bytes=20030, idle_age=14373, hard_age=65534, priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,22)
```

*对于 arp 的广播请求会发送到 table 21 中继续处理。*

* br-tun table 21 的规则

```
[root@node2 ~]# ovs-ofctl dump-flows br-tun table=21
NXST_FLOW reply (xid=0x4):
 cookie=0x8ca031df7a84a666, duration=178864.554s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=1,arp_tpa=192.168.100.2 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163e513bf7->NXM_NX_ARP_SHA[],load:0xc0a86402->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:51:3b:f7,IN_PORT
 cookie=0x8ca031df7a84a666, duration=178864.545s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=1,arp_tpa=192.168.100.6 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163e68f35c->NXM_NX_ARP_SHA[],load:0xc0a86406->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:68:f3:5c,IN_PORT
 cookie=0x8ca031df7a84a666, duration=178863.952s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=2,arp_tpa=192.168.200.2 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163ed9fcfb->NXM_NX_ARP_SHA[],load:0xc0a8c802->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:d9:fc:fb,IN_PORT
 cookie=0x8ca031df7a84a666, duration=178863.945s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=2,arp_tpa=192.168.200.3 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163eb4a4c8->NXM_NX_ARP_SHA[],load:0xc0a8c803->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:b4:a4:c8,IN_PORT
 cookie=0x8ca031df7a84a666, duration=85536.411s, table=21, n_packets=0, n_bytes=0, idle_age=65534, hard_age=65534, priority=1,arp,dl_vlan=2,arp_tpa=192.168.200.8 actions=load:0x2->NXM_OF_ARP_OP[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],load:0xfa163e715ac6->NXM_NX_ARP_SHA[],load:0xc0a8c808->NXM_OF_ARP_SPA[],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],mod_dl_src:fa:16:3e:71:5a:c6,IN_PORT
 cookie=0x8ca031df7a84a666, duration=178874.171s, table=21, n_packets=32, n_bytes=1542, idle_age=14475, hard_age=65534, priority=0 actions=resubmit(,22)
```

**终于找到了！就是在这里实现了 arp responser 的功能**

* 对于 arp 请求目的地址为 *192.168.200.8* 的处理如下（在原数据包的基础上进行修改）：
 1. `load:0x2->NXM_OF_ARP_OP[]`：表示将构造的ARP包的类型设置为ARP Reply
 2. `move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[]`：表示将Request中的源MAC地址作为Reply中的目的MAC地址
 3. `move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[]`：表示将表示将Request中的源IP地址作为Reply中的目的IP地址
 4. `load:0xfa163e715ac6->NXM_NX_ARP_SHA[]`：表示将Request请求的目的虚拟机的MAC地址作为Reply中的源MAC地址
 5. `load:0xc0a8c808->NXM_OF_ARP_SPA[]`：表示将表示将Request请求的目的虚拟机的IP地址作为Reply中的源IP地址
 6. `move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[]`：表示将ARP Request数据包的源MAC地址作为ARP Reply数据包的目的MAC地址
 7. `mod_dl_src:fa:16:3e:71:5a:c6`：表示将 `fa:16:3e:71:5a:c6`（vm2 的 mac 地址） 作为ARP Reply数据包的源MAC地址
 8. `IN_PORT`：表示将封装好ARP Reply从ARP Request的入端口送出，返回给源虚拟机

[OVS ARP Responder – Theory and Practice](https://assafmuller.com/2014/05/21/ovs-arp-responder-theory-and-practice/)

* 构造完 arp responser 后，该数据包会通过 *patch-tun* 发送到 br-int 网桥中，根据 table 0 的规则，该数据包会被正常的转发，这样子 vm1 就会收到 arp reply 了。
