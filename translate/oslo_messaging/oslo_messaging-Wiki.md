# oslo_messaging

## WIKI

Oslo messaging 提供两种独立的 API。

1. oslo.messaging.rpc 用于实现客户端-服务器远程过程调用

2. oslo.messaging.notify 用于发出和处理事件通知

### oslo.messaging.rpc

#### 概念

* Server：服务端提供客户端可以使用RPC接口

* Client：客户端调用服务端提供的方法

* Exchange：一个包含了各个项目主题（topic）的容器。

* Topic：一个RPC接口的标识；服务器端在某个 topic 上监控方法调用，而客户端在某个 topic 上调用方法。

* Namespace：服务器可以在一个 topic 上公开多组方法，其中每组方法的范围在命名空间之下。有一个默认的空名称空间。

* Method：一个方法由一个名字和一组命名的参数组成。

* API version：每个命名空间都有一个版本号，当命名空间的接口变化时，这个版本号也会相应增加。向前兼容的修改只需要更改小版本号，向前不兼容的更改需要更改大版本号。服务器可以支持多个不兼容的版本。客户端可以在调用方法时请求最低版本。

* Transport：将RPC请求传递到服务器并将答复返回给客户端的底层消息传递系统，而不需要客户端和服务器需要知道消息系统的任何细节

#### 使用方式

当我们有多个服务器侦听交换机内的主题的方法调用时，其中交换和主题名称都是客户端所熟知的。那么会有下面三种调度方式：

1. 调度将以循环方式将客户端请求分发到其中一个监听服务器。

2. 客户端可以指定一个特定的服务器来调用一个方法。

3. 客户端可以指定所有的服务器端来调用一个方法

#### 调用方法的类型

cast - 该方法是异步调用的，没有结果返回给调用者
call - 该方法被同步调用，结果返回给调用者

### Transports

Transports 是对底层消息传输系统的抽象封装，目前支持两个基于AMQP的实现（kombu/rabbitmq和qpid）和一个ZeroMQ实现。

#### Kombu/RabbitMQ 配置参数

* 配置的参数主要描述了该如何连接到 RabbitMQ:

 * host
 * port
 * userid
 * password
 * virtual_host

* 当一个连接失败时，有一些参数可以控制重试的行为：

 * retry_interval
 * retry_backoff
 * max_retries

* 关于 SSL 的配置：

 * use_ssl
 * ssl_version
 * keyfile
 * certfile
 * ca_certs

* 还有一个关于 AMQP 的高级参数，以允许持久化和镜像 AMQP 队列：

 * durable_queues
 * ha_queues

* 最后有趣的是，我们支持在您使用群集代理的情况下配置多个RabbitMQ代理主机名：

 * hosts = [$host]

#### Qpid 配置

* 配置基本的连接信息：

 * hostname
 * port
 * username
 * password
 * protocol (tcp or ssl)

* 更晦涩的配置参数：

 * sasl_mechanisms
 * heartbeat
 * nodelay

* 而且，再次支持群集中的多个主机：

 * hosts = [$host]

#### ZeroMQ

* 描述我们应该如何监听zmq连接：

 * bind_address
 * host
 * port
 * ipc_dir

* Tweaking/tuning:

 * contexts
 * topic_backlog

* Matchmaker configuration:

 * matchmaker (i.e. which driver to use)

* Specific to ringfile matchmaker:

 * ringfile (a path to a json file)

* Specific to the redis matchmaker:

 * host
 * port
 * password
 * heartbeat_freq
 * heartbeat_ttl

#### Transport URLs

有趣的是，kombu支持以URL的形式提供传输配置参数：

amqp://$userid:$password@$host:$port/$virtual_host

它还使用一些选项的查询参数，例如

amqp://$userid:$password@$host:$port/$virtual_host?ssl=1

我们将使用类似的模型来描述传输配置。 在简单的情况下，没有一个标准的URL属性对于特定的传输具有任何意义，我们可以做：

weirdo:///?param1=foo&param2=bar

由于某些传输将支持群集场景，其中传输必须与多个不同（但相当的）配置配合，因此我们将支持使用一组URL配置传输。

### Target

在 Target 上调用方法。 Target 由以下参数描述：

* exchange (defaults to CONF.control_exchange)
* topic
* server (optional)
* fanout (defaults to False)
* namespace (optional)
* API version (optional)


在 Topic 名称中使用星号在 AMQP 中具有特殊意义。例如：服务器可以绑定到 `topic.subtopic.*` 并接收发送到 `topic.subtopic.foo` topic 的消息。这是 AMQP 特定的基于通配符的 topic 在服务器上匹配，我们没有在 OpenStack 中使用，所以我们不应该在我们的API的服务器端允许这样的主题名称。

注意：在想要具有 “如何联系这个其他服务” 配置参数的情况下，可以在传输URL（exchange? topic?）中包含一些目标参数并不滑稽，如：

glance_transport = kombu://me:secret@foobar:3232//glance/notifications

## 实例

server 构建消息队列并给出可调用方法foo。

```
import oslo.messaging
from oslo.config import cfg
class TestEndpoint(object):
    target = oslo.messaging.Target(namespace='test', version='2.0')
    def __init__(self, server):
        self.server = server
    def foo(self, ctx, id):
        return id
oslo.messaging.set_transport_defaults('myexchange')
transport = oslo.messaging.get_transport(cfg.CONF)
target = oslo.messaging.Target(topic='myroutingkey', server='myserver')
endpoints = [TestEndpoint(None)]
server = oslo.messaging.get_rpc_server(transport, target, endpoints,
                                      executor='blocking')
server.start()
server.wait()
```

client客户端绑定通过exchange绑定到myrouting类型的队列，远程同步调用test命令空间里的foo方法。

```
import oslo.messaging
from oslo.config import cfg
oslo.messaging.set_transport_defaults('myexchange')
transport = oslo.messaging.get_transport(cfg.CONF,
                 url='rabbit://guest:guest@127.0.0.1:5672/')
target = oslo.messaging.Target(topic='myroutingkey', version='2.0', 
                               namespace='test')
client = oslo.messaging.RPCClient(transport, target)
r = client.call({}, 'foo', id='1')
print r
```

## 配置

* We have some transport-agnostic config options:

rpc_backend - choose the transport driver
control_exchange - allows e.g. having two heat deployments using the same messaging broker, simply by doing control_exchange = 'heat1'

* Then some tuning parameters:

rpc_thread_pool_size
rpc_conn_pool_size
rpc_response_timeout
rpc_cast_timeout

* Then we have a config option which should simply be part of the API, since users should never have to configure it:

allowed_rpc_exception_modules

* And this bizaroness:

fake_rabbit

## oslo.notify

notify API定义用于发出和处理事件通知的语义。

对于RPC API，有多个后端驱动程序使用不同的传输机制来实现API语义。 到目前为止，使用最广泛的后端驱动程序通知是通过与RPC消息相同的消息系统发送通知的RPC驱动程序。 然而，我们当然有可能有一个将来的通知驱动程序使用传输，这对RPC消息使用是没有意义的。