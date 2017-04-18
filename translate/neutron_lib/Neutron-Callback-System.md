# Neutron Callback System

在 neutron 中，核心和服务组件可能需要在执行某些操作期间进行协作，或者需要对某些事件的发生做出反应。 例如，当一个 Neutron 资源与多个服务相关联时，负责这些服务的组件可能需要在确定资源的正确状态需要时起积极作用。

可以通过使每个对象彼此认识来实现协作，但是这会导致紧耦合，还可以通过使用基于回调的系统来实现，其中允许相同的对象以松散的方式进行协作。

这是特别重要的，因为先进的服务，如VPN，防火墙和负载平衡器，其中每个服务的代码库独立从核心和彼此独立生活。 这意味着紧耦合不再是对象合作的实际解决方案。 除此之外，如果更多的服务是独立开发的，那么它们与 Neutron 核心之间就没有可行的整合。 回调系统及其注册表试图解决这些问题。

在面向对象的软件系统中，方法调用也称为消息传递：一个对象将消息传递给另一个对象，并且可能会也可能不会期待消息的返回。这种点对点交互可以在直接参与通信的各方之间进行，也可以通过中间人进行。然后，中间人负责跟踪谁对消息感兴趣，并在需要时向后发送消息。如前所述，使用中介有利于将通信中涉及的各方脱钩，因为现在他们只需要了解中间人;另一个好处是使用中介打开了多方通信的可能性：多于一个对象可以表达对接收相同消息的兴趣，并且可以将相同的消息传递给多个对象。为此，中间人是整个系统生命周期中存在的实体，因为它需要能够跟踪哪些兴趣与什么消息相关联。

在使用基于回调的通信的系统的设计中，需要考虑以下方面：

* 如何成为消息的消费者（即称为消息的接收端）;

* 如何成为消息的生成者（即称为在消息的发送端）;

* 如何有选择地消费/产生消息;

翻译并将其缩小到 Neutron 需求，这意味着回调系统的设计，其中消息是关于中子资源（例如网络，路由器，端口等）的生命周期事件（例如在创建之前，删除之前等），各方可以表达兴趣，了解对于特定资源来说这些事件何时发生。

让我们深入了解一些例子，而不是保持谈话的抽象，这将有助于更好地了解提供的机制背后的一些原则。

## Event payloads

对于回调事件有效载荷的 `**kwargs` 的使用已被弃用（预定在 `Queens` 中被移除），有利于如本文所述的标准化事件的有效载荷对象。

事件有效负载在 `neutron_lib.callbacks.events` 中定义，并基于消耗模式定义一组有效载荷对象。现在定义了以下事件对象：

* `EventPayload`：所有其他有效负载的基础对象，并定义事件使用的常用属性集。 对于基本有效载荷来说 `EventPayload` 可以直接用于不需要传输附加值。

* `DBEventPayload`：与数据库回调有关的负载。这些对象捕获数据库更改的前和后状态（除其他外）。

* `APIEventPayload`：与API回调有关的负载。这些对象捕获与API事件有关的细节;例如方法名称和API操作。

每个事件对象在下面的其自己的小节中有更详细的描述。

为了向后兼容，回调注册表和管理器仍然提供通知方法来传递 `**kwargs`，而且还提供了传递事件对象的 `publish` 方法。

### Event objects: EventPayload

`EventPayload` 对象是所有其他有效负载对象的父类，并定义适用于大多数事件的常用属性集。 例如，EventPayload包含context、request_body等。此外，元数据属性可用于传输尚未标准化的事件数据。虽然元数据属性在这里是可用的，但它应该仅在特殊情况下使用，例如phasing in new payload attributes.

有效载荷对象还通过 `states` 属性传输资源状态。 资源对象的这个集合跟踪与事件相关的相应资源的状态变化。 例如，数据库更改可能具有用作 `states` 的更新前和更新后的资源。跟踪状态允许消费者检查资源中的各种变化，并根据需要采取行动; 例如检查前后对象以确定增量。 状态对象类型是事件特定的; API事件可以使用python dicts作为状态对象，而数据库事件使用 资源/OVO 模型对象。

请注意，状态以及任何其他事件有效载荷属性都不会被复制;用户获得对事件有效载荷对象（状态，元数据等）的直接引用，不应由获取者修改。

### Event objects: DBEventPayload

对于 数据存储/数据库 事件，DBEventPayload 可用作载荷事件对象。 除了继承自EventPayload的属性之外，数据库有效载荷还包含一个附加的 `expect_state`。 期望的状态用于预创建/提交场景，其中发布者具有在事件有效负载中使用的资源对象（尚待持久化）。

这些事件对象适用于我们今天以前的数据库事件之前/之后的标准以及将来可能出现的任何事件。

使用示例

```
# BEFORE_CREATE:
DBEventPayload(context,
               request_body=params_of_create_request,
               resource_id=id_of_resource_if_avail,
               desired_state=db_resource_to_commit)

# AFTER_CREATE:
DBEventPayload(context,
               request_body=params_of_create_request,
               states=[my_new_copy_after_create],
               resource_id=id_of_resource)

# PRECOMMIT_CREATE:
DBEventPayload(context,
               request_body=params_of_create_request,
               resource_id=id_of_resource_if_avail,
               desired_state=db_resource_to_commit)

# BEFORE_DELETE:
DBEventPayload(context,
               states=[resource_to_delete],
               resource_id=id_of_resource)

# AFTER_DELETE:
DBEventPayload(context,
               states=[copy_of_deleted_resource],
               resource_id=id_of_resource)

# BEFORE_UPDATE:
DBEventPayload(context,
               request_body=body_of_update_request,
               states=[original_db_resource],
               resource_id=id_of_resource
               desired_state=updated_db_resource_to_commit)

# AFTER_UPDATE:
DBEventPayload(context,
               request_body=body_of_update_request,
               states=[original_db_resource, updated_db_resource],
               resource_id=id_of_resource)
```

### Event objects: APIEventPayload

对于API相关的回调函数，APIEventPayload对象可用于传输回调负载。例如，REST API资源控制器可以使用API​​事件进行前/后操作回调。

除了传输EventPayload的所有属性之外，APIEventPayload对象还包括允许API组件传递API控制器详细信息的action，method_name和collection_name payload属性。

简单用例：

```
# BEFORE_RESPONSE for create:
APIEventPayload(context, notifier_method, action,
         request_body=req_body,
         states=[create_result],
         collection_name=self._collection_name)

# BEFORE_RESPONSE for delete:
APIEventPayload(context, notifier_method, action,
         states=[copy_of_deleted_resource],
         collection_name=self._collection_name)

# BEFORE_RESPONSE for update:
APIEventPayload(context, notifier_method, action,
         states=[original, updated],
         collection_name=self._collection_name)
```

## 订阅事件

想象一下，您有实体A，B和C在路由器创建时有一些相同的业务。 A想要告诉B和C路由器已经创建，并且他们需要继续执行任何应该做的事情。 在一个无回调的世界中，这样工作就像这样：

```
# A is done creating the resource
# A gets hold of the references of B and C
# A calls B
# A calls C
B->my_random_method_for_knowing_about_router_created()
C->my_random_very_difficult_to_remember_method_about_router_created()
```

如果B和/或C改变，事情就不好处理了。在基于回调的世界中，事情变得更加统一和直截了当：

```
# B and C ask I to be notified when A is done creating the resource

# ...
# A is done creating the resource
# A gets hold of the reference to the intermediary I
# A calls I
I->notify()
```

由于B和C将表示有兴趣了解A的业务，“I” 将会将消息传递给B和C。如果B和C发生变化，A和"I"不需要更改。

实际上，这种情况将在下面的代码中体现：

```
from neutron_lib.callbacks import events
from neutron_lib.callbacks import resources
from neutron_lib.callbacks import registry


def callback1(resource, event, trigger, payload):
    print('Callback1 called by trigger: ', trigger)
    print('payload: ', payload)

def callback2(resource, event, trigger, payload):
    print('Callback2 called by trigger: ', trigger)
    print('payload: ', payload)


# B and C express interest with I
registry.subscribe(callback1, resources.ROUTER, events.BEFORE_CREATE)
registry.subscribe(callback2, resources.ROUTER, events.BEFORE_CREATE)
print('Subscribed')


# A notifies
def do_notify():
    registry.publish(resources.ROUTER, events.BEFORE_CREATE,
                     do_notify, events.EventPayload(None))


print('Notifying...')
do_notify()
```

输出为：

```
> Subscribed
> Notifying...
> Callback2 called by trigger:  <function do_notify at 0x7f2a5d663410>
> payload: <neutron_lib._callbacks.events.EventPayload object at 0x7ff9ed253510>
> Callback1 called by trigger:  <function do_notify at 0x7f2a5d663410>
> payload: <neutron_lib._callbacks.events.EventPayload object at 0x7ff9ed253510>
```

由于系统整个生命周期的中介存在，A，B和C灵活地发展其自身。

## 订阅和中止事件

有趣的是，在 neutron 方面，由于所涉及的资源的性质，某些事件可能需要被禁止发生。为此目的，基于回调的机制被设计为支持一种用例，当回调订阅特定事件时，由此产生的动作可能导致消息传播回发送方，从而使其本身可以在第一时间被警告并停止导致信息分发的活动的执行。

典型的例子是一个或多个高级服务（如VPN或防火墙）使用资源（如路由器），而不能发生像接口删除或路由器销毁这样的操作，因为资源是共享。

为了解决这种情况，引入了特殊事件 `BEFORE_*` 事件，回调可以订阅并有机会“中止”，通知时抛出异常。

由于多个回调可能表示对于特定资源的同一事件的兴趣，并且由于回调彼此独立地执行，这可能导致在异常之前发生的通知必须中止的情况。 为此，当通知过程中发生异常时， `abort_*` 事件将在之后立即传播。 回调开发人员需要确定是否需要订阅中止通知，以便恢复在初始执行回调期间执行的操作（当 `BEFORE_*` 事件触发时）。注销中止事件的回调引起的异常被忽略。下面的代码段显示了这一点：

```
from neutron_lib.callbacks import events
from neutron_lib.callbacks import exceptions
from neutron_lib.callbacks import resources
from neutron_lib.callbacks import registry


def callback1(resource, event, trigger, payload=None):
    raise Exception('I am failing!')

def callback2(resource, event, trigger, payload=None):
    print('Callback2 called by %s on event  %s' % (trigger, event))


registry.subscribe(callback1, resources.ROUTER, events.BEFORE_CREATE)
registry.subscribe(callback2, resources.ROUTER, events.BEFORE_CREATE)
registry.subscribe(callback2, resources.ROUTER, events.ABORT_CREATE)
print('Subscribed')


def do_notify():
    registry.publish(resources.ROUTER, events.BEFORE_CREATE, do_notify)

print('Notifying...')
try:
    do_notify()
except exceptions.CallbackFailure as e:
    print("Error: %s" % e)
```

输出为：

```
> Subscribed
> Notifying...
> Callback2 called by <function do_notify at 0x7f3194c7f410> on event  before_create
> Callback2 called by <function do_notify at 0x7f3194c7f410> on event  abort_create
> Error:  Callback __main__.callback1 failed with "I am failing!"
```

在这种情况下，在通知 `BEFORE_CREATE` 事件后，Callback1触发一个异常，可以用于停止在 `do_notify()` 中发生的操作。 另一方面，`Callback2` 将执行两次，一次处理`BEFORE_CREATE` 事件，一次在 `ABORT_CREATE` 事件中撤消操作。 值得注意的是，对于 `BEFORE_*` 和相应的 `ABORT_*` 事件都没有必要具有相同的回调来注册; 事实上，最好利用不同的回调来保持两个逻辑的分离。

## 取消订阅事件

有几个选项取消订阅已注册的回调：

* `clear()`：它取消订阅所有订阅的回调：这可以是有用的，特别是在卷起系统时，不再触发通知。

* `unsubscribe()`：它有选择地取消订阅特定资源的事件的回调。 回调C已经为资源R订阅了事件A，在 `unsubscribe()` 调用之后，资源R的事件A的任何通知将不会再移交给C。

* `unsubscribe_by_resource()`：表示回调C已经为资源R订阅了事件A，B和C，在 `resubscribe_by_resource()` 调用之后，与资源R相关的事件的任何通知将不会再移交给C。

* `unsubscribe_all()`：表示回调C已经订阅资源R1的事件A，B以及资源R2的事件C，D，在 `unsubscribe_all()` 调用后，关于资源R1和R2的事件的任何通知将不再被交给C。

下面的代码片段显示了这些动作中的概念：

```
from neutron_lib.callbacks import events
from neutron_lib.callbacks import exceptions
from neutron_lib.callbacks import resources
from neutron_lib.callbacks import registry


def callback1(resource, event, trigger, payload=None):
    print('Callback1 called by %s on event %s for resource %s' % (trigger, event, resource))


def callback2(resource, event, trigger, payload=None):
    print('Callback2 called by %s on event %s for resource %s' % (trigger, event, resource))


registry.subscribe(callback1, resources.ROUTER, events.BEFORE_READ)
registry.subscribe(callback1, resources.ROUTER, events.BEFORE_CREATE)
registry.subscribe(callback1, resources.ROUTER, events.AFTER_DELETE)
registry.subscribe(callback1, resources.PORT, events.BEFORE_UPDATE)
registry.subscribe(callback2, resources.ROUTER_GATEWAY, events.BEFORE_UPDATE)
print('Subscribed')


def do_notify():
    print('Notifying...')
    registry.publish(resources.ROUTER, events.BEFORE_READ, do_notify)
    registry.publish(resources.ROUTER, events.BEFORE_CREATE, do_notify)
    registry.publish(resources.ROUTER, events.AFTER_DELETE, do_notify)
    registry.publish(resources.PORT, events.BEFORE_UPDATE, do_notify)
    registry.publish(resources.ROUTER_GATEWAY, events.BEFORE_UPDATE, do_notify)


do_notify()
registry.unsubscribe(callback1, resources.ROUTER, events.BEFORE_READ)
do_notify()
registry.unsubscribe_by_resource(callback1, resources.PORT)
do_notify()
registry.unsubscribe_all(callback1)
do_notify()
registry.clear()
do_notify()
```

输出为：

```
Subscribed
Notifying...
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event before_read for resource router
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event before_create for resource router
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event after_delete for resource router
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event before_update for resource port
Callback2 called by <function do_notify at 0x7f062c8f67d0> on event before_update for resource router_gateway
Notifying...
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event before_create for resource router
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event after_delete for resource router
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event before_update for resource port
Callback2 called by <function do_notify at 0x7f062c8f67d0> on event before_update for resource router_gateway
Notifying...
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event before_create for resource router
Callback1 called by <function do_notify at 0x7f062c8f67d0> on event after_delete for resource router
Callback2 called by <function do_notify at 0x7f062c8f67d0> on event before_update for resource router_gateway
Notifying...
Callback2 called by <function do_notify at 0x7f062c8f67d0> on event before_update for resource router_gateway
Notifying...
```

## 用回调测试

提供了一个python fixture，用于需要进行单元测试并模拟回调注册表的实现。 例如，这可以用于，当您的代码发布您需要验证的回调事件时。消费者可以在其单元测试类中使用 `neutron_lib.tests.unit.callbacks.base.CallbackRegistryFixture`，而 `useFixture()` 方法传递一个 `CallbackRegistryFixture` 实例。 如果需要 mock 实际的 singleton 回调管理器，消费者可以通过 `callback_manager` kwarg 传递一个值。 例如：

```
def setUp(self):
    super(MyTestClass, self).setUp()
    self.registry_fixture = callback_base.CallbackRegistryFixture()
    self.useFixture(self.registry_fixture)
    # each test now uses an isolated callback manager
```

## FAQ

* 我可以使用回调注册表来订阅并通知非核心资源和事件吗？

 * 简短的答案是肯定的。 回调模块定义了被认为是 neutron 核心资源和事件的 literals。 但是，订阅/通知的能力不限于这些，因为您可以使用自己定义的资源或事件。只需确保使用字符串文字，因为打字错误是常见的，并且注册表不提供任何运行时验证。因此，请确保您测试代码！

* 回调和Taskflow之间的关系是什么？

 * 回调与任务流或互斥之间没有重叠; 事实上他们可以结合起来; 你可以有一个回调，并触发一个任务流。 这是一种将抽象与抽象分离的好方法，因为您可以将回调保留到位，并以任何其他方式更改任务流。

* 通知期间是否有任何订购保证？

 * 不，通过设计通知回调的顺序是完全任意的：回调函数应该彼此无关，排序不应该重要; 回调将始终被通知，并且其结果应始终是相同的，而不管其通知的顺序如何。 如果出现需要强制排序的用例，优先级可以是未来的扩展。

* 通知对象如何预期与订阅对象进行交互？

 * 通知方法实现单向通信范例：通知器发送消息而不期待响应（换句话说，它触发并忘记）。 然而，由于Python的本质，有效载荷可以被订阅对象所突变，如果您认为这是故意设计，这可能会导致代码的意外行为。 请记住，使用深度拷贝的传递值没有因为效率而被选择。 话虽如此，如果您打算通知程序对象期望响应，则通知程序本身将需要充当订户。

* 注册是线程安全吗？

 * 简短的答案是否定的：在调用回调时进行突变是不安全的（关于为什么可以在[这里](https://hg.python.org/releasing/2.7.9/file/753a8f457ddc/Objects/dictobject.c#l937)找到更多细节）。 如果“订阅”/“取消订阅”操作与执行通知循环交错，则可能发生突变。 尽管有可能事情可能最终导致恶劣的状态，但注册程序的工作正常，假设订阅是在流程生命的开始时发生的，而取消订阅（如果有）发生在最后。 在这种情况下，事情做得很糟糕的机会可能会很细。 使注册表线程安全将被视为未来的改进。

* 什么样的功能可以回调？
 
 * 任何你想要的：lambdas，'closures'，类，对象或模块的方法。例如：

```
from neutron_lib.callbacks import events
from neutron_lib.callbacks import resources
from neutron_lib.callbacks import registry


def callback1(resource, event, trigger, payload):
    print('module callback')


class MyCallback(object):

    def callback2(self, resource, event, trigger, payload):
        print('object callback')

    @classmethod
    def callback3(cls, resource, event, trigger, payload):
        print('class callback')


c = MyCallback()
registry.subscribe(callback1, resources.ROUTER, events.BEFORE_CREATE)
registry.subscribe(c.callback2, resources.ROUTER, events.BEFORE_CREATE)
registry.subscribe(MyCallback.callback3, resources.ROUTER, events.BEFORE_CREATE)

def do_notify():
    def nested_subscribe(resource, event, trigger, payload):
        print('nested callback')

    registry.subscribe(nested_subscribe, resources.ROUTER, events.BEFORE_CREATE)

    registry.publish(resources.ROUTER, events.BEFORE_CREATE,
                     do_notify, events.EventPayload(None))


print('Notifying...')
do_notify()
```
输出为：
```
Notifying...
module callback
object callback
class callback
nested callback
```