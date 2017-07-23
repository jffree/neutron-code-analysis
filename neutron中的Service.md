# Neutron 之 Service

neutron 中的 neutron-server 与 agent 的启动都是在这里孵化出来的。

*neutron/service.py*

## `class Service(n_rpc.Service)`

### `def create`

类方法，在准备好参数的情况下（未声明的情况下，使用配置文件中的值），创建一个 Service 实例

```
    @classmethod
    def create(cls, host=None, binary=None, topic=None, manager=None,
               report_interval=None, periodic_interval=None,
               periodic_fuzzy_delay=None)
```

* 参数说明：
 1. `host`: defaults to cfg.CONF.host
 2. `binary`: 可执行文件的名称，这个是被 profiler 使用的
 3. `topic`: rpc 用的 topic
 4. `manager`: 该 service 的管理器（这个是最重要的，一切的操作都是以）
 5. `report_interval`: 
 6. `periodic_interval`: 
 7. `periodic_fuzzy_delay`: 

### `def __init__`

```
    def __init__(self, host, binary, topic, manager, report_interval=None,                                                                                             
                 periodic_interval=None, periodic_fuzzy_delay=None,
                 *args, **kwargs)
```

初始化实例属性

### `def start(self)`

```
    def start(self):                                                                                                                                                   
        self.manager.init_host()
        super(Service, self).start()
        if self.report_interval:
            pulse = loopingcall.FixedIntervalLoopingCall(self.report_state)
            pulse.start(interval=self.report_interval,
                        initial_delay=self.report_interval)
            self.timers.append(pulse)

        if self.periodic_interval:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            periodic = loopingcall.FixedIntervalLoopingCall(
                self.periodic_tasks)
            periodic.start(interval=self.periodic_interval,
                           initial_delay=initial_delay)
            self.timers.append(periodic)
        self.manager.after_start()
```

1. 调用 `manager.init_host`
2. 调用 `super(Service, self).start` 来启动 RPC server 端。
2. 设定两个周期执行的任务 `report_interval` 和 `periodic_interval`
3. 调用 `manager.after_start`


### `def __getattr__(self, key)`

```
    def __getattr__(self, key):                                                                                                                                        
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)
```

### `def kill(self)`

```
    def kill(self):
        """Destroy the service object."""
        self.stop()
```

### `def stop(self)`

```
    def stop(self):                                                                                                                                                    
        super(Service, self).stop()
        for x in self.timers:
            try:
                x.stop()
            except Exception:
                LOG.exception(_LE("Exception occurs when timer stops"))
        self.timers = []
```

### `def wait(self)`

```
    def stop(self):                                                                                                                                                    
        super(Service, self).stop()
        for x in self.timers:
            try:
                x.stop()
            except Exception:
                LOG.exception(_LE("Exception occurs when timer stops"))
        self.timers = []
```

### `def wait(self)`

```
    def wait(self):                                                                                                                                                    
        super(Service, self).wait()
        for x in self.timers:
            try:
                x.wait()
            except Exception:
                LOG.exception(_LE("Exception occurs when waiting for timer"))
```

### `def reset(self)`

```
    def reset(self):                                                                                                                                                   
        config.reset_service()
```

### `def periodic_tasks(self, raise_on_error=False)`

```
    def periodic_tasks(self, raise_on_error=False):                                                                                                                    
        """Tasks to be run at a periodic interval."""
        ctxt = context.get_admin_context()
        self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)
```

### `def report_state(self)`

```
    def report_state(self):                                                                                                                                            
        """Update the state of this service."""
        # Todo(gongysh) report state to neutron server
        pass
```

## `class Service(service.Service)`

*neutron/common/rpc.py*

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

* 这个类其实是启动了一个 RPC Server 端。
 1. `topic`：self.topic
 2. `endpoint`：self.manager

## `class Service(ServiceBase)`

*oslo_service/service.py*

```
class Service(ServiceBase):
    """Service object for binaries running on hosts."""

    def __init__(self, threads=1000):
        self.tg = threadgroup.ThreadGroup(threads)

    def reset(self):
        """Reset a service in case it received a SIGHUP."""

    def start(self):
        """Start a service."""

    def stop(self, graceful=False):
        """Stop a service.                                                                                                                                             
    
        :param graceful: indicates whether to wait for all threads to finish
               or terminate them instantly
        """
        self.tg.stop(graceful)

    def wait(self):
        """Wait for a service to shut down."""
        self.tg.wait()
```


## `class ServiceBase(object)`

*oslo_service/service.py*

抽象基类，定义了 Service 的架构

```
@six.add_metaclass(abc.ABCMeta)
class ServiceBase(object):
    """Base class for all services."""
 
    @abc.abstractmethod
    def start(self):
        """Start service."""
 
    @abc.abstractmethod
    def stop(self):
        """Stop service."""

    @abc.abstractmethod
    def wait(self):
        """Wait for service to complete."""

    @abc.abstractmethod
    def reset(self):
        """Reset service.

        Called in case service running in daemon mode receives SIGHUP.
        """  
```