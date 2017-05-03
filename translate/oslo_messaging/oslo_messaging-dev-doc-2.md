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












