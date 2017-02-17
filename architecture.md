![](/assets/A-1.png)

* Neutron server 接收 api 请求。
* plugin/agent 实现请求。
* database 保存 neutron 网络状态。
* message queue 实现组件之间通信。

![](/assets/A-2.jpg)

Neutron 通过 plugin 和 agent 提供的网络服务。

plugin 位于 Neutron server，包括 core plugin 和 service plugin。

agent 位于各个节点，负责实现网络服务。

core plugin 提供 L2 功能，ML2 是推荐的 plugin。

使用最广泛的 L2 agent 是 linux bridage 和 open vswitch。

service plugin 和 agent 提供扩展功能，包括 dhcp, routing, load balance, firewall, vpn 等。

### 参考：

[两张图总结 Neutron 架构 - 每天5分钟玩转 OpenStack（74）](http://www.cnblogs.com/CloudMan6/p/5778505.html)

