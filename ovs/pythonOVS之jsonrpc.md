# python OVS 之 jsonrpc

*ovs/jsonrpc.py*

1. `Connection`：维护与 ovsdb 的连接，用于与 ovsdb 通信。
2. `Message`：封装与 ovsdb 通信所使用的消息
3. `Session`：

## `class Connection(object)`

```
class Connection(object):
    def __init__(self, stream):
        self.name = stream.name
        self.stream = stream
        self.status = 0
        self.input = ""
        self.output = ""
        self.parser = None
        self.received_bytes = 0
```

* 属性说明：
 1. `name`：链接的名称
 2. `stream`：封装 socket 的 `Stream` 的实例
 3. `status`：链接的状态（0为正常，负数为不正常）。
 4. `input`：从 ovsdb 接收到的消息
 5. `output`：准备向 ovsdb 发送的消息
 6. `parser`：json 解析器，负责解析从 ovsdb 接受到的数据。
 7. `received_bytes`：从 ovsdb 接受到的数据的字节数的大小

### `def close(self)`

关闭与 OVSDB 的连接

### `def __log_msg(self, title, msg)`

日志记录

### `def error(self, error)`

记录错误消息，并关闭 stream 的链接

### `def run(self)`

循环发送 `output` 内的数据，直至发送完毕。发送完毕的同时会清空 `output`。

### `def send(self, msg)`

调用 `run` 来发送以 `Message` 封装的消息。

### `def transact_block(self, request)`

调用 `send` 发送 request 中包含的消息，调用 `recv_block` 接受消息

### `def recv_block(self)`

不停的调用 `recv` 来接受消息，直到消息接受完成

### `def recv(self)`

调用 `stream.recv` 来接收消息。

### `def __process_msg(self)`

将从 ovsdb 接受到的 json 数据解析完成后转化为 `Message` 封装的格式。

## `class Message(object)`

与 OVSDB 通讯的消息封装（JSON-RPC）。

```
    T_REQUEST = 0               # Request.
    T_NOTIFY = 1                # Notification.
    T_REPLY = 2                 # Successful reply.
    T_ERROR = 3                 # Error reply.

    __types = {T_REQUEST: "request",
               T_NOTIFY: "notification",
               T_REPLY: "reply",
               T_ERROR: "error"}

    _next_id = 0
```

消息的类型分为四种：请求消息、通知消息；成功回复、错误回复。

id：代表了本次请求的 id

### `def __init__(self, type_, method, params, result, error, id)`

```
    def __init__(self, type_, method, params, result, error, id):
        self.type = type_
        self.method = method
        self.params = params
        self.result = result
        self.error = error
        self.id = id
```

### `def _create_id()`

```
    @staticmethod
    def _create_id():
        this_id = Message._next_id
        Message._next_id += 1
        return this_id
```

### `def create_request(method, params)`

创建一个请求消息。

`method`：请求调用 OVSDB 的方法
`params`：请求方法的参数

### ` def create_notify(method, params)`

创建一个通知消息。

`method`：通知调用 OVSDB 的方法
`params`：通知方法的参数

### `def create_reply(result, id)`

创建一个回复消息（`result`）。

### `def create_error(error, id)`

创建一个错误消息（`error`）。

### `def type_to_string(type_)`

```
    @staticmethod
    def type_to_string(type_):
        return Message.__types[type_]
```

### `def to_json(self)`

将封装的消息（`Message`）转化为 json 格式

### `def from_json(json)`

将一个 json 格式（dict）消息，封装为 `Message` 格式

### `def is_valid(self)`

验证 Message 封装的消息是否合法



## `class Session(object)`

```
    def __init__(self, reconnect, rpc):
        self.reconnect = reconnect
        self.rpc = rpc
        self.stream = None
        self.pstream = None
        self.seqno = 0
```

* 参数说明：
 1. `reconnect`：FSM 实例
 2. `rpc`：通过监听连接来创建（与 pstream 配合使用）
 3. `stream`：建立并维持与 ovsdb server 的连接，然后用 rpc 进行封装。
 4. `pstream`：建立在本机的监听，当有连接请求进来时，在连接的基础上创建 rpc 实例。

* 解析
 1. FSM 用来维持 session 中连接的状态
 2. session 中的连接有两种状态：一种是主动去连接 server 端，通过 stream 实现；一种是在本机建立监听（pstream），当有请求进来时，与之建立连接
 3. session 中的两种连接都要用 rpc 进行封装，方便与 server 进行通讯

`seqno`：序号，建立连接时序号增加，取消连接时序号增加

### `def open(name)`

静态方法。根据 name 创建一个 FSM，在此 FSM 的基础上创建一个 Session 实例。

### `def open_unreliably(jsonrpc)`

在已有的 rpc 基础上创建 Session 实例。

### `def is_connected(self)`

是否建立连接（是否有 rpc 的存在）

### `def close(self)`

关闭所有存在的连接和监听

### `def run(self)`

业务处理方法。

* 对于 `pstream` 来说，接受连接申请，创建 rpc
* 对于 `stream` 来说，主动去连接 server 创建 rpc
* 对于 `rpc` 来说，执行与 server 通讯的任务。

根据 FSM 的反馈，判断下一步要进行的动作。

1. 若需要进行连接，则调用 `__connect` 方法
2. 若需要断开连接，则调用 `__disconnect` 方法
3. 若需要 PROBE ，则调用 `self.rpc` 调用 server 端的 echo 方法

### `def __disconnect(self)`

断开与 server 端的连接

### `def __connect(self)`

建立与 server 端的连接

1. 若 FSM 为非 passive 模式，则创建一个 `Stream` 对象
2. 若 FSM 为 passive 模式，则创建一个 `PassiveStream` 对象

### `def wait(self, poller)`

阻塞等待，直到有消息发送或者接收。

### `def get_backlog(self)`

准备向 server 端发送消息的大小

### `def send(self, msg)`

调用 rpc 发送 msg 消息

### `def recv(self)`

接受从 server 端回复的消息

### `def recv_wait(self, poller)`

等待有可接收的消息

### `def is_alive(self)`

检查是否有与 server 端的连接存在。

### `def force_reconnect(self)`

强制 FSM 改变到 `Reconnect` 状态，从而引发与 server 端连接的重置。