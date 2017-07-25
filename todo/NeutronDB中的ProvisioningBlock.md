# Neutron Db ProvisioningBlock

参考：*doc/source/devref/provisioning_blocks.rst*

介绍：

* 某一资源对象由创建到可用可能会经历多个步骤，当这些步骤全部完成时才能将这个资源对象置为可用状态。
但是，当这些步骤未执行完毕时，需要将这个资源进行锁定（provisioning block），意味着此资源还未可用。

实例：

1. 一个创建 port 的请求发送到 neutron-server，neutron-server 会做一下几点操作：
 1. 创建 port 的数据库信息
 2. 通知 dhcp agent 有 port 需要创建
 3. 在 l2 agent（neutron-server） 创建 port
 4. 将该 port 置为锁定（provisioning block）状态（有两个，分别是 l2 agent 和 dhcp agent）
2. l2 agent 完成 port 的创建，取消对其对该 port 的锁定；
3. dhcp agent 完成对 port 的配置，取消其对该 port 的锁定；
4. 当所有的锁定都解除时，会调用回调方法发送 `PROVISIONING_COMPLETE` 的通知，neutron-server 接到通知后，会做最后的处理。