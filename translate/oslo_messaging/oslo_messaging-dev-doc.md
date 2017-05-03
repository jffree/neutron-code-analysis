# oslo_messaging developer doc

## Transport

### `oslo_messaging.get_transport(conf, url=None, allowed_remote_exmods=None, aliases=None)`

Transport 对象的工厂方法。

此方法将从用户配置中的 Transport 配置构建一个传输对象，并可选择传输URL。

如果传输 URL 作为参数提供，则其中包含的任何传输配置优先。 如果没有提供传输URL，但是在用户配置中提供了传输URL，则该URL将替代URL参数。 在这两种情况下，传输URL中未提供的任何配置可能取决于用户配置中的各个配置参数。

传输URL的示例可能是：

```
rabbit://me:passwd@host:5672/virtual_host
```

Transport URL 可以作为字符串或TransportURL对象传递。

**Parameters:**
	
* conf (cfg.ConfigOpts) – the user configuration
* url (str or TransportURL) – a transport URL
* allowed_remote_exmods (list) – a list of modules which a client using this transport will deserialize remote exceptions from
* aliases (dict) – DEPRECATED: A map of transport alias to transport name

### `class oslo_messaging.Transport(driver)`

A messaging transport.

这是个封装底层传输驱动的不透明的句柄

它具有单个 `conf` 属性，它是用于构造传输对象的 `cfg.ConfigOpts` 实例。

### `class oslo_messaging.TransportURL(conf, transport=None, virtual_host=None, hosts=None, aliases=None, query=None)`

A parsed transport URL.

传输URL的格式如下：

```
transport://user:pass@host:port[,userN:passN@hostN:portN]/virtual_host?query
```

即该方案选择传输驱动程序，可以在netloc中包含多个主机，路径部分是 `virtual_host` 分区路径，并且查询部分包含一些驱动程序特定的选项，可以从静态配置中覆盖相应的值。

**Parameters:**
	
* conf (oslo.config.cfg.ConfigOpts) – a ConfigOpts instance
* transport (str) – a transport name for example ‘rabbit’
* virtual_host (str) – a virtual host path for example ‘/’
* hosts (list) – a list of TransportHost objects
* aliases (dict) – DEPRECATED: a map of transport alias to transport name
* query (dict) – a dictionary of URL query parameters

### `classmethod parse(conf, url=None, aliases=None)`

Parse an url.

假设URL的格式为：

```
transport://user:pass@host:port[,userN:passN@hostN:portN]/virtual_host?query
```

然后解析URL并返回一个TransportURL对象。

Netloc按照以下顺序进行解析：

* 它首先被'，'分割，以便支持多个主机

* 所有主机都应使用用户名/密码同时指定。在缺少规格的情况下，用户名和密码将被省略：

```
user:pass@host1:port1,host2:port2

[
  {"username": "user", "password": "pass", "host": "host1:port1"},
  {"host": "host2:port2"}
]
```

如果没有提供url，conf.transport_url会被解析。

### `class oslo_messaging.TransportHost(hostname=None, port=None, username=None, password=None)`

解析的传输URL的主机元素。

### `oslo_messaging.set_transport_defaults(control_exchange)`

设置消息传输配置选项的默认值。

**Parameters:**	

* control_exchange (str) – 默认交换在哪个主题范围内

### Forking Processes and oslo.messaging Transport objects

oslo.messaging不能确保为库消费者分配共享相同传输对象的进程是安全的，因为它依赖于不能确保的不同的第三方库。在某些情况下，有些驱动程序可以正常工作：

* rabbit: works only if no connection have already been established.
* amqp1: works

## Executors

执行者控制接收到的消息如何安排服务器进行处理。此调度可以是同步的或异步的。

同步执行器将处理服务器线程上的消息。 这意味着服务器一次只能处理一个消息。 其他传入的消息将不会被处理，直到当前消息完成处理。 例如，在RPCServer的情况下，一次只会调用一个方法调用。 同步执行器保证消息按照接收的顺序完成处理。

异步执行器将同时处理接收到的消息。 服务器线程不会被消息处理阻止，并且可以继续服务传入的消息。 没有订购保证 - 消息处理可能会以与收到的不同的顺序完成。 执行器可能被配置为限制一次处理的最大消息数。

### Available Executors

#### blocking

执行者使用 caller 同步执行调用。

这为调用者提供了一个看起来像执行器的接口，但是将在调用者线程中执行调用，而不是在外部进程/线程中执行调用，因为这种类型的功能有助于提供...

它会收集关于分析后执行的提交的统计资料...

#### eventlet

使用绿色线程池的执行程序异步执行调用。

See: https://docs.python.org/dev/library/concurrent.futures.html and http://eventlet.net/doc/modules/greenpool.html for information on how this works.

收集关于分析后执行的提交的统计资料...

#### threading

执行者使用线程池来异步执行调用。

收集关于分析后执行的提交的统计资料...

See: https://docs.python.org/dev/library/concurrent.futures.html

## Target

### `class oslo_messaging.Target(exchange=None, topic=None, namespace=None, version=None, server=None, fanout=None, legacy_namespaces=None)`

标识 message 的目的地。

Target 封装了所有信息，以确定消息应发送在哪里或服务器正在侦听哪些消息。

封装在Target对象中的信息的不同子集与API的各个方面相关：

1. an RPC Server’s target:
 * topic and server is required; exchange is optional
2. an RPC endpoint’s target:
 * namespace and version is optional
3. an RPC client sending a message:
 * topic is required, all other attributes optional
4. a Notification Server’s target:
 * topic is required, exchange is optional; all other attributes ignored
5. a Notifier’s target:
 * topic is required, exchange is optional; all other attributes ignored

其属性有：

**Parameters:**

* exchange (str) – 主题范围。将未指定的默认值保留到control_exchange配置选项。

* topic (str) – 标识由服务器公开的接口集的名称。多个服务器可以监听主题，并将消息分派到以尽力而为的循环方式选择的服务器之一（除非fanout为True）。

* namespace (str) – 标识由服务器公开的特定RPC接口（即一组方法）。默认界面没有命名空间标识符，并称为空命名空间。

version (str) – RPC接口具有与它们相关联的主要版本号。向前兼容的修改只需要更改小版本号，向前不兼容的更改需要更改大版本号。服务器可以支持多个不兼容的版本。客户端可以在调用方法时指定最低版本。

* server (str) – RPC客户端可以请求将消息定向到特定服务器，而不仅仅是侦听主题的服务器池中的一个。

* fanout (bool) – 客户可能会要求通过将fanout设置为True而将消息的副本传递给所有监听主题的服务器。

legacy_namespaces (list of strings) – 服务器始终接受通过'namespace'参数指定的消息，并且还可以接受通过此参数定义的消息。应该使用此选项在滚动升级期间安全地切换命名空间。

### Target Versions

目标版本号格式为Major.Minor。对于X.Y版本的给定消息，服务器必须被标记为能够处理版本A.B的消息，其中A == X和B> = Y.

对于几乎全新的API来说主版本号应该增加。次要版本号将增加，以便向现有API的向后兼容更改。 向后兼容的更改可能是添加新方法，向现有方法添加参数（但不需要），或更改现有参数的类型（但仍处理旧类型）。

如果没有指定版本，则默认为“1.0”。

在RPC的情况下，如果您希望允许您的服务器接口发展，以便客户端不需要在与服务器锁定的情况下进行更新，则应注意实现服务器向后兼容的更改，并让客户端指定接口版本。

向端点添加新方法是向后兼容的更改，并且端点的目标的版本属性应该从X.Y到X.Y + 1。 在客户端，新的RPC调用应具有指定的特定版本，以指示必须为要支持的方法实现的最小API版本。 例如：

```
def get_host_uptime(self, ctxt, host):
    cctxt = self.client.prepare(server=host, version='1.1')
    return cctxt.call(ctxt, 'get_host_uptime')
```

在这种情况下，版本'1.1'是支持get_host_uptime（）方法的第一个版本。

向RPC方法添加新参数可以向后兼容。应该碰到服务器端的 endpoint 版本。方法的实现不能指望参数存在：

```
def some_remote_method(self, arg1, arg2, newarg=None):
    # The code needs to deal with newarg=None for cases
    # where an older client sends a message without it.
    pass
```

在客户端，应按照示例1进行相同的更改。应指定支持新参数的最小版本。














