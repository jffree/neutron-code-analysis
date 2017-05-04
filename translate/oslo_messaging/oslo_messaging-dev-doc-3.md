# oslo_messaging developer doc

## RPC Client

### `class oslo_messaging.RPCClient(transport, target, timeout=None, version_cap=None, serializer=None, retry=None)`

A class for invoking methods on remote RPC servers.

RPCClient类负责通过消息传输向远程RPC服务器发送方法调用和接收返回值。

支持两种RPC模式：RPC calls 和RPC casts。

当RPC方法不向调用者返回值时，将使用RPC casts。当从该方法预期返回值时使用RPC calls。有关更多信息，请参阅 `cast()` 和 `call()` 方法。

默认的 traget 用于向 RPCClient 构造函数提供所有后续 call 和 cast。客户端使用 target 来控制 RPC 请求如何传送到服务器。 如果仅设置目标  topic (and optionally exchange)，则可以由正在侦听该 topic (and exchange) 的任何服务器对 RPC 进行服务。如果多个服务器正在监听该 topic/exchange，则使用尽力而为的循环算法来选择一个服务器。 或者，客户端可以将Target 的服务器属性设置为特定服务器的名称，以将RPC请求发送到一个特定服务器。 在RPC转换的情况下，RPC请求可以通过将Target的fanout属性设置为True来广播到监听Target的 topic/exchange 的所有服务器。

虽然在构建时设置了默认目标，但可以使用 `prepare()` 方法覆盖单个方法调用的目标属性。

方法调用由请求上下文字典，方法名称和参数字典组成。

该类旨在通过将其包装在另一个类中来使用，该类为子类提供使用 `call()` 或 `cast()` 执行远程调用的方法：

```
class TestClient(object):

    def __init__(self, transport):
        target = messaging.Target(topic='test', version='2.0')
        self._client = messaging.RPCClient(transport, target)

    def test(self, ctxt, arg):
        return self._client.call(ctxt, 'test', arg=arg)
```

使用 `prepare()` 方法覆盖默认目标的某些属性的示例：

```
def test(self, ctxt, arg):
    cctxt = self._client.prepare(timeout=10)
    return cctxt.call(ctxt, 'test', arg=arg)
```

但是，这个类可以直接使用，而不用另外一个类。例如：

```
transport = messaging.get_transport(cfg.CONF)
target = messaging.Target(topic='test', version='2.0')
client = messaging.RPCClient(transport, target)
client.call(ctxt, 'test', arg=arg)
```

但是这可能仅在有限的情况下有用，因为包装类通常有助于使代码更加清晰。

#### `call(ctxt, method, **kwargs)`

Invoke a method and wait for a reply.

`call()` 方法用于调用有返回值的 RPC 方法。由于只允许单个返回值，因此无法在 fanout target 上调用 `call()`。

`call()` 将阻塞调用线程，直到消息传输提供返回值，发生超时或发生不可恢复的错误。

`call()` 保证RPC请求是“最多一次”完成的，这确保了呼叫永远不会被重复。 但是，如果在返回值到达之前调用失败或超时，则无法保证该方法是否被调用。

由于 `call()` 阻塞直到完成 RPC 方法，所以保证来自同一线程的 `call()` 被按顺序处理。

方法参数必须是原始类型或客户端序列化程序支持的类型（如果有）。类似地，请求上下文必须是dict，除非客户机的序列化器支持序列化其他类型。

远程RPC端点方法引发的任何错误的语义都是非常微妙的。

首先，如果远程异常包含在 `allow_remote_exmods messaging.get_transport()` 参数中列出的其中一个模块中，则此异常将由 `call()` 重新生成。 但是，这种本地重新引发的远程异常与本地引发的同一异常类型是可以区分的，因为重新引发的远程异常被修改，使得它们的类名称以 `_Remote` 后缀结尾，以便您可以执行以下操作：

```
if ex.__class__.__name__.endswith('_Remote'):
    # Some special case for locally re-raised remote exceptions
```

其次，如果远程异常不是来自 `allowed_remote_exmods` 列表中列出的模块，则会引发一个`messaging.RemoteError` 异常，其中包含远程异常的所有详细信息。

**Parameters:**	
* ctxt (dict) – a request context dict
* method (str) – the method name
* kwargs (dict) – a dict of method arguments

**Raises:**
	
* MessagingTimeout
* RemoteError
* MessageDeliveryFailure

#### `can_send_version(version=<object object>)`

检查版本是否与版本上限兼容。

#### `cast(ctxt, method, **kwargs)`

Invoke a method without blocking for a return value.

`cast()` 方法用于调用不返回值的 RPC 方法。 `cast()` RPC请求可能会通过将 fanout Target 属性设置为 True 来广播给所有监听给定主题的服务器。

`cast()` 操作是尽力而为的：`cast()` 将阻塞调用线程，直到消息传输接受 RPC 请求方法，但是 `cast()` 不会验证服务器已调用RPC方法。 `cast()` 确实保证方法不会在目的地执行两次（例如“最多一次”执行）。

连续 cast 没有排序保证，即使在同一目的地的 cast 中。因此，方法可以以与它们被 cast 的顺序不同的顺序执行。

方法参数必须是原始类型或客户端序列化程序支持的类型（如果有）。

类似地，请求上下文必须是dict，除非客户机的序列化器支持序列化其他类型。

**Parameters:**
	
* ctxt (dict) – a request context dict
* method (str) – the method name
* kwargs (dict) – a dict of method arguments

**Raises:**	

* MessageDeliveryFailure 如果消息传输不能接受请求。

#### `prepare(exchange=<object object>, topic=<object object>, namespace=<object object>, version=<object object>, server=<object object>, fanout=<object object>, timeout=<object object>, version_cap=<object object>, retry=<object object>)`

Prepare a method invocation context.

使用此方法覆盖单个方法调用的客户端属性。例如：

```
def test(self, ctxt, arg):
    cctxt = self.prepare(version='2.5')
    return cctxt.call(ctxt, 'test', arg=arg)
```

**Parameters:**	

* exchange (str) – see Target.exchange
* topic (str) – see Target.topic
* namespace (str) – see Target.namespace
* version (str) – requirement the server must support, see Target.version
* server (str) – send to a specific server, see Target.server
* fanout (bool) – send to all servers on topic, see Target.fanout
* timeout (int or float) – an optional default timeout (in seconds) for call()s
* version_cap (str) – raise a RPCVersionCapError version exceeds this cap
* retry (int) – an optional connection retries configuration: None or -1 means to retry forever. 0 means no retry is attempted. N means attempt at most N retries.

### `exception oslo_messaging.RemoteError(exc_type=None, value=None, traceback=None)`

表示远程端点方法引发异常。

包含原始异常的类型，原始异常的值和追溯的字符串表示形式。这些作为连接字符串发送给父级，因此打印异常包含所有相关信息。

## Notification Driver

通过消息发送通知的通知驱动程序。

消息传递驱动程序向通知侦听器发布通知消息。

驱动程序将阻塞通知程序的线程，直到通知消息传递到消息传递。不能保证通知消息将被通知侦听器使用。

通知消息“最多一次”发送 - 确保它们不被重复。

如果在发送通知时与消息传递服务的连接不活动，则此驱动程序将阻止等待连接完成。 如果连接无法完成，驱动程序将尝试重新建立该连接。 默认情况下，它将无限期地继续，直到连接完成。 但是，在给定的重试次数之后，重试参数可用于使通知发送失败并发送MessageDeliveryFailure。

### `class oslo_messaging.notify.messaging.MessagingDriver(conf, topics, transport, version=1.0)`

使用1.0消息格式发送通知。

此驱动程序通过配置的消息传输发送通知，但没有任何消息信封（也称为消息格式1.0）。

只有在现有消费者部署不支持2.0消息格式的情况下，才应使用此驱动程序。

### `class oslo_messaging.notify.messaging.MessagingV2Driver(conf, **kwargs)`

Send notifications using the 2.0 message format.

### `class oslo_messaging.notify.notifier.Driver(conf, topics, transport)`

通知的基本驱动程序

#### `notify(ctxt, msg, priority, retry)`

send a single notification with a specific priority

**Parameters:**
	
* ctxt – current request context
* msg (str) – message to be sent
* priority (str) – priority of the message
* retry (int) – connection retries configuration (used by the messaging driver): None or -1 means to retry forever. 0 means no retry is attempted. N means attempt at most N retries.

## Notification Listener

通知侦听器用于处理由通知器发送的使用消息传递驱动程序的通知消息。

通知侦听器在所提供的 target 中订阅 topic - and optionally exchange。通知客户端发送给目标 topic/exchange 的通知消息由侦听器接收。

如果多个听众订阅同一个目标，那么只有其中一个收听者才会收到通知。使用尽力而为的循环算法从组中选择接收侦听器。

通过为侦听器指定池名称，可以稍微改变此传递模式。 具有相同池名称的侦听器的行为就像订阅同一主题/交换机的侦听器组中的子组一样。 每个侦听器子组将收到该子组的一个成员将要消费的通知的副本。 因此，将传递通知的多个副本，一个到没有池名称（如果存在）的侦听器组，以及共享相同池名称的一个到每个子组的侦听器。

请注意，并不是所有的传输驱动程序都实现了对监听器池的支持。如果指定了池名称为 `get_notification_listener()`，那些不支持池的驱动程序将引发 `NotImplementedError`。

通知侦听器暴露了多个端点，每个端点都包含一组方法。 每个方法的名称对应于通知的优先级。 当收到通知时，将其发送到类似通知的优先级的方法。例如：信息通知被调度到 `info()` 方法等。

可选地，通知端点可以定义 `NotificationFilter`。与过滤器规则不匹配的通知消息将不会传递到端点的方法。

**端点方法的参数是：**由客户端提供的请求上下文，通知消息的publisher_id，event_type，有效载荷和元数据。 元数据参数是包含唯一的message_id和时间戳的映射。

端点方法可以显式地返回 `oslo_messaging.NotificationResult.HANDLED` 来确认消息或 `oslo_messaging.NotificationResult.REQUEUE` 来重新排队消息。 请注意，并不是所有的传输驱动程序都支持重新安排。 为了使用此功能，应用程序应通过将 `allow_requeue = True` 传递给 `get_notification_listener()` 来声明该功能可用。 如果驱动程序不支持重新启动，则会在此时引发 `NotImplementedError`。

仅当所有端点返回 `oslo_messaging.NotificationResult.HANDLED` 或 `None` 时才会确认该消息。

每个通知侦听器与执行器相关联，该执行器控制如何接收和发送传入的通知消息。 默认情况下，使用最简单的执行器 - 阻塞执行器。 此执行程序处理服务器线程上的入站通知，阻止其处理其他通知，直到完成当前通知。 有关其他类型的执行程序的说明，请参阅Executor文档。

注意：如果使用“eventlet”执行器，则线程和时间库需要进行monkepatched。

通知监听器具有 `start()`，`stop()` 和 `wait()` 消息，以开始处理请求，停止处理请求，并在监听器停止后等待所有进程内请求完成。

要创建通知侦听器，您提供 a transport, list of targets and a list of endpoints.。

可以通过调用 `get_notification_transport()` 方法获得传输：

```
transport = messaging.get_notification_transport(conf)
```

这将根据用户的消息传递配置加载适当的传输驱动程序。有关详细信息，请参阅 `get_notification_transport()` 。

具有多个端点的通知侦听器的简单示例可能是：

```
from oslo_config import cfg
import oslo_messaging


class NotificationEndpoint(object):
    filter_rule = oslo_messaging.NotificationFilter(
        publisher_id='^compute.*')

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        do_something(payload)


class ErrorEndpoint(object):
    filter_rule = oslo_messaging.NotificationFilter(
        event_type='^instance\..*\.start$',
        context={'ctxt_key': 'regexp'})

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        do_something(payload)

transport = oslo_messaging.get_notification_transport(cfg.CONF)
targets = [
    oslo_messaging.Target(topic='notifications'),
    oslo_messaging.Target(topic='notifications_bis')
]
endpoints = [
    NotificationEndpoint(),
    ErrorEndpoint(),
]
pool = "listener-workers"
server = oslo_messaging.get_notification_listener(transport, targets,
                                                  endpoints, pool=pool)
server.start()
server.wait()
```

通过提供串行化器对象，侦听器可以反序列化来自基本类型的请求上下文和参数。

### `oslo_messaging.get_notification_listener(transport, targets, endpoints, executor='blocking', serializer=None, allow_requeue=False, pool=None)`

Construct a notification listener

执行器参数控制如何接收和发送传入消息。默认情况下，使用最简单的执行器 - 阻塞执行器。

如果使用了eventlet执行器，则线程和时间库需要进行monkepatched。

**Parameters:**
	
* transport (Transport) – the messaging transport
* targets (list of Target) – the exchanges and topics to listen on
* endpoints (list) – a list of endpoint objects
* executor (str) – name of message executor - available values are ‘eventlet’, ‘blocking’ and ‘threading’
* serializer (Serializer) – an optional entity serializer
* allow_requeue (bool) – whether NotificationResult.REQUEUE support is needed
* pool (str) – the pool name

**Raises:**
	
* NotImplementedError

### `oslo_messaging.get_batch_notification_listener(transport, targets, endpoints, executor='blocking', serializer=None, allow_requeue=False, pool=None, batch_size=None, batch_timeout=None)`

Construct a batch notification listener

执行器参数控制如何接收和发送传入消息。默认情况下，使用最简单的执行器 - 阻塞执行器。

如果使用了eventlet执行器，则线程和时间库需要进行monkepatched。

**Parameters:**
	
* transport (Transport) – the messaging transport
* targets (list of Target) – the exchanges and topics to listen on
* endpoints (list) – a list of endpoint objects
* executor (str) – name of message executor - available values are ‘eventlet’, ‘blocking’ and ‘threading’
* serializer (Serializer) – an optional entity serializer
* allow_requeue (bool) – whether NotificationResult.REQUEUE support is needed
* pool (str) – the pool name
* batch_size (int) – number of messages to wait before calling endpoints callacks
* batch_timeout (int) – number of seconds to wait before calling endpoints callacks

**Raises:**
	
* NotImplementedError