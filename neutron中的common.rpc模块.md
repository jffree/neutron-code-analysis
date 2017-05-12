# neutron中的 common.rpc 模块

提供 rpc 服务所需要的基础功能

## 服务端发送异常时，客户端用来处理这些异常的模块

```
ALLOWED_EXMODS = [
    exceptions.__name__,
    lib_exceptions.__name__,
]
EXTRA_EXMODS = []

def add_extra_exmods(*args):
    EXTRA_EXMODS.extend(args)


def clear_extra_exmods():
    del EXTRA_EXMODS[:]


def get_allowed_exmods():
    return ALLOWED_EXMODS + EXTRA_EXMODS
```

## transport 别名

```
TRANSPORT_ALIASES = {
    'neutron.openstack.common.rpc.impl_fake': 'fake',
    'neutron.openstack.common.rpc.impl_qpid': 'qpid',
    'neutron.openstack.common.rpc.impl_kombu': 'rabbit',
    'neutron.openstack.common.rpc.impl_zmq': 'zmq',
    'neutron.rpc.impl_fake': 'fake',
    'neutron.rpc.impl_qpid': 'qpid',
    'neutron.rpc.impl_kombu': 'rabbit',
    'neutron.rpc.impl_zmq': 'zmq',
}
```

## rpc 中的解析器

*用于将 rpc 的通用上下文转化为 neutron 的上下文。*

```
class RequestContextSerializer(om_serializer.Serializer):
    """This serializer is used to convert RPC common context into
    Neutron Context.
    """
    def __init__(self, base=None):
        super(RequestContextSerializer, self).__init__()
        self._base = base

    def serialize_entity(self, ctxt, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(ctxt, entity)

    def deserialize_entity(self, ctxt, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(ctxt, entity)

    def serialize_context(self, ctxt):
        _context = ctxt.to_dict()
        prof = profiler.get()
        if prof:
            trace_info = {
                "hmac_key": prof.hmac_key,
                "base_id": prof.get_base_id(),
                "parent_id": prof.get_id()
            }
            _context['trace_info'] = trace_info
        return _context

    def deserialize_context(self, ctxt):
        rpc_ctxt_dict = ctxt.copy()
        trace_info = rpc_ctxt_dict.pop("trace_info", None)
        if trace_info:
            profiler.init(**trace_info)
        return context.Context.from_dict(rpc_ctxt_dict)
```

* 主要方法有两个：
 1. `serialize_context`：将neutron格式的上下文转化为字典格式
 2. `deserialize_context`：将普通字典格式的上下文转化为neutron格式（`Context`）

## rpc 服务的初始化

```
def init(conf):
    global TRANSPORT, NOTIFICATION_TRANSPORT, NOTIFIER
    exmods = get_allowed_exmods()
    TRANSPORT = oslo_messaging.get_transport(conf,
                                             allowed_remote_exmods=exmods,
                                             aliases=TRANSPORT_ALIASES)
    NOTIFICATION_TRANSPORT = oslo_messaging.get_notification_transport(
        conf, allowed_remote_exmods=exmods, aliases=TRANSPORT_ALIASES)
    serializer = RequestContextSerializer()
    NOTIFIER = oslo_messaging.Notifier(NOTIFICATION_TRANSPORT,
                                       serializer=serializer)
```

* 初始化创建 `TRANSPORT`、`NOTIFICATION_TRANSPORT`、`NOTIFIER`，其中：
 1. `TRANSPORT` 为 rpc 服务所用的 transport
 2. `NOTIFICATION_TRANSPORT` 为 notifier 所用的 transport
 3. `NOTIFIER` 为 notifier 实例

该方法会在所有的 agent 和 neutron-server 启动的时候被调用。

## nutron 中的 rpc client 封装

```
class _ContextWrapper(object):
    """Wraps oslo messaging contexts to set the timeout for calls.

    This intercepts RPC calls and sets the timeout value to the globally
    adapting value for each method. An oslo messaging timeout results in
    a doubling of the timeout value for the method on which it timed out.
    There currently is no logic to reduce the timeout since busy Neutron
    servers are more frequently the cause of timeouts rather than lost
    messages.
    """
    _METHOD_TIMEOUTS = collections.defaultdict(
        lambda: TRANSPORT.conf.rpc_response_timeout)

    @classmethod
    def reset_timeouts(cls):
        cls._METHOD_TIMEOUTS.clear()

    def __init__(self, original_context):
        self._original_context = original_context

    def __getattr__(self, name):
        return getattr(self._original_context, name)

    def call(self, ctxt, method, **kwargs):
        # two methods with the same name in different namespaces should
        # be tracked independently
        if self._original_context.target.namespace:
            scoped_method = '%s.%s' % (self._original_context.target.namespace,
                                       method)
        else:
            scoped_method = method
        # set the timeout from the global method timeout tracker for this
        # method
        self._original_context.timeout = self._METHOD_TIMEOUTS[scoped_method]
        try:
            return self._original_context.call(ctxt, method, **kwargs)
        except oslo_messaging.MessagingTimeout:
            with excutils.save_and_reraise_exception():
                wait = random.uniform(0, TRANSPORT.conf.rpc_response_timeout)
                LOG.error(_LE("Timeout in RPC method %(method)s. Waiting for "
                              "%(wait)s seconds before next attempt. If the "
                              "server is not down, consider increasing the "
                              "rpc_response_timeout option as Neutron "
                              "server(s) may be overloaded and unable to "
                              "respond quickly enough."),
                          {'wait': int(round(wait)), 'method': scoped_method})
                ceiling = TRANSPORT.conf.rpc_response_timeout * 10
                new_timeout = min(self._original_context.timeout * 2, ceiling)
                if new_timeout > self._METHOD_TIMEOUTS[scoped_method]:
                    LOG.warning(_LW("Increasing timeout for %(method)s calls "
                                    "to %(new)s seconds. Restart the agent to "
                                    "restore it to the default value."),
                                {'method': scoped_method, 'new': new_timeout})
                    self._METHOD_TIMEOUTS[scoped_method] = new_timeout
                time.sleep(wait)


class BackingOffClient(oslo_messaging.RPCClient):
    """An oslo messaging RPC Client that implements a timeout backoff.

    This has all of the same interfaces as oslo_messaging.RPCClient but
    if the timeout parameter is not specified, the _ContextWrapper returned
    will track when call timeout exceptions occur and exponentially increase
    the timeout for the given call method.
    """
    def prepare(self, *args, **kwargs):
        ctx = super(BackingOffClient, self).prepare(*args, **kwargs)
        # don't enclose Contexts that explicitly set a timeout
        return _ContextWrapper(ctx) if 'timeout' not in kwargs else ctx
```

* `BackingOffClient` 是对 oslo_messaging 中 `RPCClient` 的封装，并重写了 `prepare` 方法。

* 调用`prepare` 方法时（每次 `call` 和 `cast` 都会调用），在不手动指定上下文的 `timeout` 属性时，会返回一个对上下文的封装类（`_ContextWrapper`）实例。

* `_ContextWrapper` 重写了 `call` 方法，在原有的上下文的 `call` 方法中增加了对超时的处理（会根据超时时间，自动增加rpc的等待响应时间）。


## 获取客户端

```
def get_client(target, version_cap=None, serializer=None):
    assert TRANSPORT is not None
    serializer = RequestContextSerializer(serializer)
    return BackingOffClient(TRANSPORT,
                            target,
                            version_cap=version_cap,
                            serializer=serializer)
```

* 这就是获取了一个 `BackingOffClient` 的实例

## 获取 server

```
def get_server(target, endpoints, serializer=None):
    assert TRANSPORT is not None
    serializer = RequestContextSerializer(serializer)
    return oslo_messaging.get_rpc_server(TRANSPORT, target, endpoints,
                                         'eventlet', serializer)
```

## 获取 notifier

```
def get_notifier(service=None, host=None, publisher_id=None):
    assert NOTIFIER is not None
    if not publisher_id:
        publisher_id = "%s.%s" % (service, host or cfg.CONF.host)
    return NOTIFIER.prepare(publisher_id=publisher_id)
```

## 连接管理

```
# NOTE(salv-orlando): I am afraid this is a global variable. While not ideal,
# they're however widely used throughout the code base. It should be set to
# true if the RPC server is not running in the current process space. This
# will prevent get_connection from creating connections to the AMQP server
RPC_DISABLED = False

class Connection(object):

    def __init__(self):
        super(Connection, self).__init__()
        self.servers = []

    def create_consumer(self, topic, endpoints, fanout=False):
        target = oslo_messaging.Target(
            topic=topic, server=cfg.CONF.host, fanout=fanout)
        server = get_server(target, endpoints)
        self.servers.append(server)

    def consume_in_threads(self):
        for server in self.servers:
            server.start()
        return self.servers

    def close(self):
        for server in self.servers:
            server.stop()
        for server in self.servers:
            server.wait()


class VoidConnection(object):

    def create_consumer(self, topic, endpoints, fanout=False):
        pass

    def consume_in_threads(self):
        pass

    def close(self):
        pass


# functions
def create_connection():
    # NOTE(salv-orlando): This is a clever interpretation of the factory design
    # patter aimed at preventing plugins from initializing RPC servers upon
    # initialization when they are running in the REST over HTTP API server.
    # The educated reader will perfectly be able that this a fairly dirty hack
    # to avoid having to change the initialization process of every plugin.
    if RPC_DISABLED:
        return VoidConnection()
    return Connection()
```

* 重点在 `Connection` 的实现了：
 1. `create_consumer`：创建 rpc server，即在 rpc 的 server 端创建 consumer
 2. `consume_in_threads`：启动所有的 server
 3. `close`：关闭所有的 server

## `Service` 这个会在 l3_agent 和 dhcp_agent 启动时用到

```
@profiler.trace_cls("rpc")
class Service(service.Service):
    """Service object for binaries running on hosts.

    A service enables rpc by listening to queues based on topic and host.
    """
    def __init__(self, host, topic, manager=None, serializer=None):
        super(Service, self).__init__()
        self.host = host
        self.topic = topic
        self.serializer = serializer
        if manager is None:
            self.manager = self
        else:
            self.manager = manager

    def start(self):
        super(Service, self).start()

        self.conn = create_connection()
        LOG.debug("Creating Consumer connection for Service %s",
                  self.topic)

        endpoints = [self.manager]

        self.conn.create_consumer(self.topic, endpoints)

        # Hook to allow the manager to do other initializations after
        # the rpc connection is created.
        if callable(getattr(self.manager, 'initialize_service_hook', None)):
            self.manager.initialize_service_hook(self)

        # Consume from all consumers in threads
        self.conn.consume_in_threads()

    def stop(self):
        # Try to shut the connection down, but if we get any sort of
        # errors, go ahead and ignore them.. as we're shutting down anyway
        try:
            self.conn.close()
        except Exception:
            pass
        super(Service, self).stop()
```