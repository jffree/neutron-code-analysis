# Neutron Messaging Callback System

Neutron已经有一个用于**进程内资源回调**的[回调系统](https://docs.openstack.org/developer/neutron-lib/devref/callbacks.html)，发布者和订阅者能够发布和订阅资源事件。

该系统是不同的，并且旨在通过消息 fanout 机制用于**进程间回调**。

在 neutron 中，代理可能需要订阅具体的资源细节，这些资源可能会随时间而变化。 此消息回传系统的目的是允许代理订阅这些资源，而不需要扩展修改现有的RPC调用或创建新的RPC消息。

有几个资源可以从这个系统中受益：

* QoS policies;
* Security Groups.

使用远程发布者/订户模式，可以使用 fanout 消息向所有感兴趣的节点发布关于此类资源的信息，从而最小化代理到服务器的消息传递请求，因为代理程序在其整个生命周期中获得订阅（除非它们取消订阅）。

在一个代理中，对同一资源事件可能有多个订户回调，资源更新将从单个消息分派到订户回调。 任何更新都会出现在单个消息中，在每个接收代理上只执行单个 oslo 版本的对象反序列化。

这种发布/订阅机制高度依赖于传递的资源的格式。 这就是为什么库只允许版本化的对象被发布和订阅。oslo 版本的对象允许对象版本下降/上转换。 [2](https://docs.openstack.org/developer/neutron/devref/rpc_callbacks.html#vo-mkcompat) [3](https://docs.openstack.org/developer/neutron/devref/rpc_callbacks.html#vo-mkcptests)

对于VO的版本化架构，请看这里：[4](https://docs.openstack.org/developer/neutron/devref/rpc_callbacks.html#vo-versioning)

`versioned_objects` 使用 `obj_to_primitive（target_version = ..）` 和`primitive_to_obj()` [1](https://docs.openstack.org/developer/neutron/devref/rpc_callbacks.html#ov-serdes) 进行序列化/反序列化，内部用于在消息传递之前或之后转换或检索对象。

序列化的版本对象如下所示：

```
{'versioned_object.version': '1.0',
 'versioned_object.name': 'QoSPolicy',
 'versioned_object.data': {'rules': [
                                     {'versioned_object.version': '1.0',
                                      'versioned_object.name': 'QoSBandwidthLimitRule',
                                      'versioned_object.data': {'name': u'a'},
                                      'versioned_object.namespace': 'versionedobjects'}
                                     ],
                           'uuid': u'abcde',
                           'name': u'aaa'},
 'versioned_object.namespace': 'versionedobjects'}
```

## 滚动升级策略

在本节中，我们假设标准Neutron升级过程，这意味着首先升级服务器，然后升级代理：

[More information about the upgrade strategy.](https://docs.openstack.org/developer/neutron/devref/upgrade.html)

我们提供一种自动方法，可以避免由管理员手动固定和解压缩版本，这可能容易出错。

### 资源拉取请求

资源提取请求将始终 ok，因为底层资源RPC确实提供了请求的资源 id/ids 的版本。服务器将首先升级，因此它将始终能够满足代理请求的任何版本。

### 资源推送通知

代理商将订阅 neutron-vo-<resource_type>-<version> fanout 队列，其中携带有他们所知道的版本的更新对象。他们知道的版本取决于他们开始的运行时Neutron版本的对象。

当服务器升级时，它应该能够立即计算每个对象的代理版本的普查（我们将在稍后一节中为此定义一个机制）。 它将使用普查在资源类型的所有版本跨度上发送 fanout 消息。

例如，如果 neutron 服务器知道它具有版本 1.0 的 rpc-callback 感知代理和资源类型 A 的版本1.2，则任何更新都将被发送到 neutron-vo-A_1.0 和 neutron-vo-A_1.2 。

TODO（mangelajo）：验证升级完成后，随着旧代理程序的消失，中子服务器停止生成新的消息 cast，任何未使用的消息传递资源（队列，交换机等）都将被释放。Otherwise document the need for a neutron-server restart after rolling upgrade has finished if we want the queues cleaned up.

#### 利用代理状态报告发现对象版本

我们向代理数据库添加一行以跟踪代理已知对象和版本号。这类似于配置列的实现。

代理报告不仅启动了现在的配置，还报告了其订阅的对象类型/版本对，它们存储在数据库中，并可用于请求它的任何 neutron 服务器：

```
'resource_versions': {'QosPolicy': '1.1',
                      'SecurityGroup': '1.0',
                      'Port': '1.0'}
```

如果安装了qos插件，`QosPolicy` 有一个 `Liberty` 代理的子集，则需要 `QosPolicy：1.0`。我们能够通过二进制名称（包括在报告中）来识别它们：

* ‘neutron-openvswitch-agent’
* ‘neutron-sriov-nic-agent’

这个转换是在 Mitaka 中处理的，但是在 Newton 中它不再处理了，因为只支持一个主要的版本步骤升级。

#### 版本发现

利用上述机制，考虑到需要QoSpolicy 1.0的 `neutron-openvswitch-agent` 和  `neutron-sriov-agent` 的例外，我们发现每个推送通知发送的版本子集。

处于关闭状态的代理将从此计算中排除。我们在这个计算中使用一个扩展超时代理，以确保我们处于安全的一面，特别是如果部署者标记了超时时间较短的代理。

从 Mitaka 开始，任何通过此API对版本化对象感兴趣的代理应报告他们感兴趣的资源/版本元组（他们订阅的资源类型/版本对）。

对此RPC机制感兴趣的插件必须继承AgentDbMixin，因为此机制目前仅用于从代理程序中使用，同时可以将其扩展为在必要时从其他组件使用。

The AgentDbMixin provides:

```
def get_agents_resource_versions(self, tracker):
   ...
```

##### 缓存机制

缓存每个对象的版本子集，以避免在每次推送时发出数据库请求，因为我们假设所有旧代理程序在升级时都已经注册。

缓存子集在neutron.api.rpc.callbacks.version_manager.VERSIONS_TTL之后重新评估（将版本集降低为代理升级）。

As a fast path to update this cache on all neutron-servers when upgraded agents come up (or old agents revive after a long timeout or even a downgrade) the server registering the new status update notifies the other servers about the new consumer resource versions via cast.

必须发送所有计算版本集的所有通知，否则未升级的代理将不会收到。

将通知发送到任何 fanout  队列是安全的，因为如果没有代理正在侦听，它们将被丢弃。

## 每个资源类型的主题名称RPC端点

neutron-vo-<resource_class_name>-<version>

将来，我们可能希望通过动态获取oslo消息来支持订阅主题，那么我们可能希望使用：

neutron-vo-<resource_class_name>-<resource_id>-<version> instead,

或者相当于一些等同的东西，这样可以使接收器的细粒度只能获得有趣的信息。

## 订阅资源

想象一下，您有代理A，它只需要处理一个具有关联的安全组的新端口和QoS策略。

代理代码处理端口更新可能如下所示：

```
from neutron.api.rpc.callbacks.consumer import registry
from neutron.api.rpc.callbacks import events
from neutron.api.rpc.callbacks import resources


def process_resource_updates(context, resource_type, resource_list, event_type):

    # send to the right handler which will update any control plane
    # details related to the updated resources...


def subscribe_resources():
    registry.register(process_resource_updates, resources.SEC_GROUP)

    registry.register(process_resource_updates, resources.QOS_POLICY)

def port_update(port):

    # here we extract sg_id and qos_policy_id from port..

    sec_group = registry.pull(resources.SEC_GROUP, sg_id)
    qos_policy = registry.pull(resources.QOS_POLICY, qos_policy_id)
```

相关方法是：

* `register(callback, resource_type)`: subscribes callback to a resource type.

回调函数将接收以下参数：

* context: the neutron context that triggered the notification.
* resource_type: the type of resource which is receiving the update.
* resource_list: list of resources which have been pushed by server.
* event_type: will be one of CREATED, UPDATED, or DELETED, see neutron.api.rpc.callbacks.events for details.

通过底层的oslo_messaging对接收器动态主题的支持，我们无法实现每个 `resource type + resource id` 主题，rabbitmq似乎可以没有痛苦处理了10000个主题，但是创建100个不同主题的oslo_messaging接收者似乎崩溃了。

我们可能稍后再考虑一下，以避免代理接收到对他们无趣的资源更新。

## 取消订阅资源

To unsubscribe registered callbacks:

* `unsubscribe(callback, resource_type)`: unsubscribe from specific resource type.
* `unsubscribe_all()`: unsubscribe from all resources.

## 发送资源事件

在服务器端，资源更新可以来自任何地方，服务插件，扩展，任何更新，创建或销毁资源，并且是订阅代理人感兴趣的任何内容。

预计回调将收到资源列表。 当列表中的资源属于相同的资源类型时，会发送单次推送RPC消息; 如果列表包含不同资源类型的对象，则每种类型的资源都会分组发送，并分别发送，每个类型推送一个RPC消息。 在接收方，列表中的资源始终属于同一类型。 换句话说，异构对象列表的服务器端推送将导致总线上的N个消息和N个客户端回调调用，其中N是给定列表中的唯一资源类型的数量，例如。 L（A，A，B，C，C，C）将分为L1（A，A），L2（B），L3（C，C，C）

注意：在单独的资源列表将不会传递给消费者的订单方面不保证。

服务器/发布方可能如下所示：

```
from neutron.api.rpc.callbacks.producer import registry
from neutron.api.rpc.callbacks import events

def create_qos_policy(...):
    policy = fetch_policy(...)
    update_the_db(...)
    registry.push([policy], events.CREATED)

def update_qos_policy(...):
    policy = fetch_policy(...)
    update_the_db(...)
    registry.push([policy], events.UPDATED)

def delete_qos_policy(...):
    policy = fetch_policy(...)
    update_the_db(...)
    registry.push([policy], events.DELETED)
```

## References

[1]	https://github.com/openstack/oslo.versionedobjects/blob/ce00f18f7e9143b5175e889970564813189e3e6d/oslo_versionedobjects/tests/test_objects.py#L410
[2]	https://github.com/openstack/oslo.versionedobjects/blob/ce00f18f7e9143b5175e889970564813189e3e6d/oslo_versionedobjects/base.py#L474
[3]	https://github.com/openstack/oslo.versionedobjects/blob/ce00f18f7e9143b5175e889970564813189e3e6d/oslo_versionedobjects/tests/test_objects.py#L114
[4]	https://github.com/openstack/oslo.versionedobjects/blob/ce00f18f7e9143b5175e889970564813189e3e6d/oslo_versionedobjects/base.py#L248