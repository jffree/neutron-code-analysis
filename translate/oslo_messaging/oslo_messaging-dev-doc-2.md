# oslo_messaging developer doc

## RPC Server

RPC服务器公开了一些端点，每个端点都包含一组方法，这些方法可以由客户端通过给定 transport 远程调用。

To create an RPC server, you supply a transport, target and a list of endpoints.

只需调用 `get_transport()` 方法即可获得 transport：

```
transport = messaging.get_transport(conf)
```

这将根据用户的消息传递配置加载适当的传输驱动程序。有关详细信息，请参阅 `get_transport()`。

在创建RPC服务器时，Target 提供的 topic, server name和要监听的交换机（可选）。有关这些属性的详细信息，请参阅Target。

多个RPC服务器可以同时听同一topic (and exchange)。有关在这种情况下如何将RPC请求分发到“服务器”的详细信息，请参阅RPCClient。

每个端点对象可能具有可以设置命名空间和版本字段的目标属性。 默认情况下，我们使用'空名称空间'和版本1.0。传入的请求方法将被分配到第一个匹配的命名空间和兼容版本号的端点。

调用的方法的第一个参数始终是客户端提供的请求上下文。剩余的参数是客户端提供给方法的参数。 端点方法可能返回一个值。如果是这样，RPC服务器将通过传输将返回的值发送回请求的客户端。

执行器参数控制如何接收和分发传入的消息。 默认情况下，使用最简单的执行器 - 阻塞执行器。 此执行程序处理服务器线程上的入站RPC请求，阻止其处理其他请求，直到完成当前请求。 这包括在方法返回结果时将回复消息发送到传输的时间。 有关其他类型的执行程序的说明，请参阅Executor文档。

**注意：**如果使用“eventlet”执行器，则线程和时间库需要进行monkepatched。

RPC回复操作是尽力而为的：服务器将考虑包含回复成功发送的消息，一旦被消息传输接受。 服务器不保证RPC客户端处理回复。 如果发送失败，将记录错误，服务器将继续处理传入的RPC请求。

方法调用的参数和从方法返回的值是python原始类型。 然而，消息中的数据的实际编码可能不是原始形式（例如，消息有效载荷可以是使用JSON编码为ASCII字符串的字典）。 串行器对象用于将传入的编码消息数据转换为原始类型。 串行器也用于将返回值从原始类型转换为适用于消息有效载荷的编码。

RPC服务器具有 `start()`，`stop()` 和 `wait()` 方法来开始处理请求，停止处理请求，并在服务器停止后等待所有进程内请求完成。

具有多个端点的RPC服务器的简单示例可能是：

```
from oslo_config import cfg
import oslo_messaging
import time

class ServerControlEndpoint(object):

    target = oslo_messaging.Target(namespace='control',
                                   version='2.0')

    def __init__(self, server):
        self.server = server

    def stop(self, ctx):
        if self.server:
            self.server.stop()

class TestEndpoint(object):

    def test(self, ctx, arg):
        return arg

transport = oslo_messaging.get_transport(cfg.CONF)
target = oslo_messaging.Target(topic='test', server='server1')
endpoints = [
    ServerControlEndpoint(None),
    TestEndpoint(),
]
server = oslo_messaging.get_rpc_server(transport, target, endpoints,
                                       executor='blocking')
try:
    server.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server")

server.stop()
server.wait()
```

### `oslo_messaging.get_rpc_server(transport, target, endpoints, executor='blocking', serializer=None, access_policy=None)`

构造一个RPC服务器。

**Parameters:**

* transport (Transport) – the messaging transport
* target (Target) – the exchange, topic and server to listen on
* endpoints (list) – a list of endpoint objects
* executor (str) – name of message executor - available values are ‘eventlet’, ‘blocking’ and ‘threading’
* serializer (Serializer) – an optional entity serializer
* access_policy (RPCAccessPolicyBase) – an optional access policy. Defaults to LegacyRPCAccessPolicy

### `class oslo_messaging.RPCAccessPolicyBase`

确定可以通过RPC调用哪些端点方法

### `class oslo_messaging.LegacyRPCAccessPolicy`

传统访问策略允许RPC访问所有可调用的端点方法，包括私有方法（前缀为“_”的方法）

### `class oslo_messaging.DefaultRPCAccessPolicy`

默认访问策略阻止RPC调用私有方法（以_ _'为前缀的方法）

注意：`LegacyRPCAdapterPolicy` 当前需要是默认值，而我们有依赖于暴露私有方法的项目。

### `class oslo_messaging.ExplicitRPCAccessPolicy`

需要被装饰的端点方法以允许发送的策略

### `class oslo_messaging.RPCDispatcher(endpoints, serializer, access_policy=None)`

了解RPC消息的消息分派器。

`MessageHandlingServer` 通过传递一个可调用的调度程序来构建，该调度程序在每次接收到消息时都会使用上下文和消息字典进行调用。

`RPCDispatcher` 是一个理解RPC消息格式的调度程序。调度程序查看消息中的命名空间，版本和方法值，并将其与可用端点列表进行匹配。

端点可能具有描述由该对象公开的方法的命名空间和版本的目标属性。

RPCDispatcher可能有一个access_policy属性，它决定要分派哪些端点方法。默认的access_policy调度端点对象上的所有公共方法。

### `class oslo_messaging.MessageHandlingServer(transport, dispatcher, executor='blocking')`

用于处理消息的服务器。

将传输连接到分派器，该分派器知道如何使用执行器来处理消息，执行器知道应用程序要创建新任务。

* `reset()`

Reset service.

Called in case service running in daemon mode receives SIGHUP.

* `start(*args, **kwargs)`

Start handling incoming messages.

此方法使服务器开始轮询传入的传入消息并将其传递给调度程序。消息处理将继续，直到调用 `stop()` 方法。

执行器控制服务器如何与应用程序 I/O 处理策略集成 - 它可以选择轮询新进程中的消息，线程或协作计划协作，或者简单地通过向事件循环注册回调。 类似地，执行者可以选择在新线程，协程或简单的当前线程中分派消息。

* `stop(*args, **kwargs)`

Stop handling incoming messages.

一旦此方法返回，服务器将不会处理新的传入消息。 但是，服务器可能仍在处理某些消息，并且与此服务器相关联的底层驱动程序资源仍在使用中。 有关详细信息，请参阅“wait”。

* `wait(*args, **kwargs)`

Wait for message processing to complete.

调用 `stop()` 后，仍然可能存在一些尚未完全处理的现有消息。 `wait()` 方法阻塞，直到所有消息处理完成。

一旦完成，与此服务器相关联的底层驱动程序资源将被释放（如关闭无用的网络连接）。

### `oslo_messaging.expected_exceptions(*exceptions)`

Decorator for RPC endpoint methods that raise expected exceptions.

使用此装饰器标记端点方法允许声明RPC服务器不应该认为是致命的预期异常，而不是像在真实错误情况下生成一样。

请注意，这将导致列出的异常包装在由RPC服务器内部使用的 `ExpectedException` 中。 RPC客户端将看到原始的异常类型。

### `oslo_messaging.expose(func)`

Decorator for RPC endpoint methods that are exposed to the RPC client.

如果调度程序的 `access_policy` 设置为 `ExplicitRPCAccessPolicy`，则需要显式地显示端点方法：

```
# foo() cannot be invoked by an RPC client
def foo(self):
    pass

# bar() can be invoked by an RPC client
@rpc.expose
def bar(self):
    pass
```

### `exception oslo_messaging.ExpectedException`

封装由RPC端点引发的预期异常

仅实例化此异常会记录当前的异常信息，这些异常信息将被传回给RPC客户端而无需特殊记录。