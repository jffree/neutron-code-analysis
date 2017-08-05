# Neutron 中 network 隔离的实现

* neutron 是个多租户的环境，每个租户可以用多个网络，那么 neutron 中时如何保证这些网络是互相隔离互不影响的呢？

* 计算节点的图例如下：

![](../img/compute1.png)

*vm1 所在的网络为 net1，`qr-0b1f0748-fd` 为 net1 的网关，`qr-19096480-60` 为 net2 的网关。 *

* 答：是通过在 br-int 交换机中设置 tag 来隔离的。
 1. 我们将 br-int 各个 port 的 tag 成为 local valn
 2. 各个 network 的 vlan id (tunnel id) 我们用 segmentation_id 来表示（当然像 flat 这类的网络是没有 segmentation id 的）。
 3. 从上面的图例我们可以看到，`qvo9c2639b3-02` 与 `qr-0b1f0748-fd` 在 br-int 中的 tag 同为 1。这意味着如果交换机是正常转发模式（NORMAL）的话：
  1. 从 `qvo9c2639b3-02` 传进来的数据包只能由 `qr-0b1f0748-fd` 接收。
  2. 从 `qvo9c2639b3-02` 传进来的数据包不会由 `qr-19096480-60` 接收。
  3. 这就意味着 net1 和 net2 是隔离开的，net1 的数据包不会传递到 net2 中。
* 实现细节：
 1. 使用同一 network 的 port 会被分配同样的 tag，这样子同一 network 内的 port 就可以互相访问
 2. 使用不同 network 的 port 会被分配不同的 tag，这样子不同 network 内的 port 就互相不可见
 3. l2 agent 会维护一个 `_local_vlan_hints` 的字典变量，这个变量里面记录了 port tag 与 network id 的对应关系。













