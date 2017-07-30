# OVS 流表的建立

## 普通流表

### br-int

1. 在 `OVSIntegrationBridge.setup_default_table` 中建立了下面几个 flow entity
 1. `cookie=0xa5e7242f14aacf4c, duration=1023.245s, table=23, n_packets=0, n_bytes=0, idle_age=65534, priority=0 actions=drop`
 2. `cookie=0xa5e7242f14aacf4c, duration=1099.072s, table=0, n_packets=16804, n_bytes=1973390, idle_age=1301, priority=0 actions=NORMAL`
 3. `cookie=0xa5e7242f14aacf4c, duration=1156.038s, table=24, n_packets=0, n_bytes=0, idle_age=65534, priority=0 actions=drop`





### br-tun

1. 在 `OVSTunnelBridge.setup_default_table` 中建立了下面几个 flow entity
 1. `cookie=0x89b1024fe5e42035, duration=2.783s, table=0, n_packets=0, n_bytes=0, idle_age=2, priority=1,in_port=1 actions=resubmit(,2)`
 2. `cookie=0xa7296f7c2d2464bf, duration=54.514s, table=0, n_packets=0, n_bytes=0, idle_age=54, priority=0 actions=drop`
 3. `cookie=0xa7296f7c2d2464bf, duration=46.730s, table=2, n_packets=0, n_bytes=0, idle_age=46, priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)`（对于单播包，转发到 20）
 4. `cookie=0xa7296f7c2d2464bf, duration=46.725s, table=2, n_packets=0, n_bytes=0, idle_age=46, priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,22)`（对于组播包，转发到 22）
 5. `cookie=0xa7296f7c2d2464bf, duration=247.890s, table=4, n_packets=0, n_bytes=0, idle_age=247, priority=0 actions=drop`
 6. `cookie=0xa7296f7c2d2464bf, duration=46.713s, table=10, n_packets=0, n_bytes=0, idle_age=46, priority=1 actions=learn(table=20,hard_timeout=300,priority=1,cookie=0xa7296f7c2d2464bf,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:OXM_OF_IN_PORT[]),output:1`



### br-ex

1. 在 `OVSPhysicalBridge.setup_default_table` 中建立了下面几个 flow entity
 1. `cookie=0x84ee7d746b40273d, duration=939.154s, table=0, n_packets=0, n_bytes=0, idle_age=939, priority=0 actions=NORMAL`


## l2 population

### br-int

### br-tun

1. 在 `OVSTunnelBridge.setup_default_table` 中建立了下面几个 flow entity
 1. `cookie=0xa7296f7c2d2464bf, duration=46.734s, table=2, n_packets=0, n_bytes=0, idle_age=46, priority=1,arp,dl_dst=ff:ff:ff:ff:ff:ff actions=resubmit(,21)`



### br-ex

## dvr mode

### br-int

1. 在 `OVSDVRNeutronAgent.setup_dvr_flows` 中：
 1. `cookie=0xa8aa161778c6d26a, duration=1440.919s, table=23, n_packets=0, n_bytes=0, idle_age=1440, priority=0 actions=drop`
 2. `cookie=0xa8aa161778c6d26a, duration=1465.096s, table=1, n_packets=0, n_bytes=0, idle_age=1465, priority=1 actions=drop`
 3. `cookie=0xa8aa161778c6d26a, duration=1486.974s, table=2, n_packets=0, n_bytes=0, idle_age=1486, priority=1 actions=drop`
 4. `cookie=0xa8aa161778c6d26a, duration=1520.804s, table=0, n_packets=21, n_bytes=2478, idle_age=33, priority=1 actions=NORMAL`
 5. `cookie=0xa8aa161778c6d26a, duration=1520.800s, table=0, n_packets=0, n_bytes=0, idle_age=1520, priority=2,in_port=1 actions=drop`






### br-tun


### br-ex






## 参考

[Neutron 理解 (4): Neutron OVS OpenFlow 流表 和 L2 Population [Netruon OVS OpenFlow tables + L2 Population]](http://www.cnblogs.com/sammyliu/p/4633814.html)