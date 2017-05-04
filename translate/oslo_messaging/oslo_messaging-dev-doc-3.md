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
















