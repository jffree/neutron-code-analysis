# neutron 之 callback system

*neutron/callbacks* 模块

* *resources.py*

这里声明了一些资源

* *events.py*

这里声明了一些事件

* *exceptions.py*

这里声明了一些异常

* *manager.py* 

这个类声明了整个 callback system 的管理类，callback system 的就是来靠这个类来实现的。

* *registery.py*

对 callback system 管理类的封装，保证整个 neutron 的声明周期中只有一个管理类的实例存在。

## `class CallbacksManager(object)`

*neutron callback system 的管理类*

### `def __init__(self)`

初始化方法

```
    def __init__(self):
        self.clear()
```

### `def clear(self)`

```
    def clear(self):
        """Brings the manager to a clean slate."""
        self._callbacks = collections.defaultdict(dict)
        self._index = collections.defaultdict(dict)
```

* `_callbacks` 保存资源、事件、回调方法的对应关系
* `_index` 保存回调方法、资源、事件的对应关系，但是用作快速超找

### `def subscribe(self, callback, resource, event)`

```
    def subscribe(self, callback, resource, event):
        """Subscribe callback for a resource event.

        The same callback may register for more than one event.

        :param callback: the callback. It must raise or return a boolean.
        :param resource: the resource. It must be a valid resource.
        :param event: the event. It must be a valid event.
        """
        LOG.debug("Subscribe: %(callback)s %(resource)s %(event)s",
                  {'callback': callback, 'resource': resource, 'event': event})

        callback_id = _get_id(callback)
        try:
            self._callbacks[resource][event][callback_id] = callback
        except KeyError:
            # Initialize the registry for unknown resources and/or events
            # prior to enlisting the callback.
            self._callbacks[resource][event] = {}
            self._callbacks[resource][event][callback_id] = callback
        # We keep a copy of callbacks to speed the unsubscribe operation.
        if callback_id not in self._index:
            self._index[callback_id] = collections.defaultdict(set)
        self._index[callback_id][resource].add(event)
```

为 `resoure` 资源的 `event` 事件注册 `callbacks` 回调函数。

### `def _find(self, callback)`

```
    def _find(self, callback):
        """Return the callback_id if found, None otherwise."""
        callback_id = _get_id(callback)
        return callback_id if callback_id in self._index else None
```

查找 `callback` 的订阅的 `callback_id`

### `def unsubscribe(self, callback, resource, event)`

```
    def unsubscribe(self, callback, resource, event):
        """Unsubscribe callback from the registry.

        :param callback: the callback.
        :param resource: the resource.
        :param event: the event.
        """
        LOG.debug("Unsubscribe: %(callback)s %(resource)s %(event)s",
                  {'callback': callback, 'resource': resource, 'event': event})

        callback_id = self._find(callback)
        if not callback_id:
            LOG.debug("Callback %s not found", callback_id)
            return
        if resource and event:
            del self._callbacks[resource][event][callback_id]
            self._index[callback_id][resource].discard(event)
            if not self._index[callback_id][resource]:
                del self._index[callback_id][resource]
                if not self._index[callback_id]:
                    del self._index[callback_id]
        else:
            value = '%s,%s' % (resource, event)
            raise exceptions.Invalid(element='resource,event', value=value)
```

取消为 `resoure` 资源的 `event` 事件注册 `callbacks` 回调函数。

### `def unsubscribe_by_resource(self, callback, resource)`

```
    def unsubscribe_by_resource(self, callback, resource):
        """Unsubscribe callback for any event associated to the resource.

        :param callback: the callback.
        :param resource: the resource.
        """
        callback_id = self._find(callback)
        if callback_id:
            if resource in self._index[callback_id]:
                for event in self._index[callback_id][resource]:
                    del self._callbacks[resource][event][callback_id]
                del self._index[callback_id][resource]
                if not self._index[callback_id]:
                    del self._index[callback_id]
```

取消为 `resoure` 资源注册 `callbacks` 回调函数。

### `def unsubscribe_all(self, callback)` 

```
    def unsubscribe_all(self, callback):
        """Unsubscribe callback for all events and all resources.


        :param callback: the callback.
        """
        callback_id = self._find(callback)
        if callback_id:
            for resource, resource_events in self._index[callback_id].items():
                for event in resource_events:
                    del self._callbacks[resource][event][callback_id]
            del self._index[callback_id]
```

取消所有 `callback` 的订阅。

### `def _notify_loop(self, resource, event, trigger, **kwargs)`

```
    def _notify_loop(self, resource, event, trigger, **kwargs):
        """The notification loop."""
        errors = []
        callbacks = list(self._callbacks[resource].get(event, {}).items())
        LOG.debug("Notify callbacks %s for %s, %s",
                  callbacks, resource, event)
        # TODO(armax): consider using a GreenPile
        for callback_id, callback in callbacks:
            try:
                callback(resource, event, trigger, **kwargs)
            except Exception as e:
                abortable_event = (
                    event.startswith(events.BEFORE) or
                    event.startswith(events.PRECOMMIT)
                )
                if not abortable_event:
                    LOG.exception(_LE("Error during notification for "
                                      "%(callback)s %(resource)s, %(event)s"),
                                  {'callback': callback_id,
                                   'resource': resource, 'event': event})
                else:
                    LOG.error(_LE("Callback %(callback)s raised %(error)s"),
                              {'callback': callback_id, 'error': e})
                errors.append(exceptions.NotificationError(callback_id, e))
        return errors
```

调用所有订阅的回调函数来处理在某一资源上发生的事件，并收集错误。

### `def notify(self, resource, event, trigger, **kwargs)`

```
    @db_api.reraise_as_retryrequest
    def notify(self, resource, event, trigger, **kwargs):
        """Notify all subscribed callback(s).

        Dispatch the resource's event to the subscribed callbacks.

        :param resource: the resource.
        :param event: the event.
        :param trigger: the trigger. A reference to the sender of the event.
        """
        errors = self._notify_loop(resource, event, trigger, **kwargs)
        if errors:
            if event.startswith(events.BEFORE):
                abort_event = event.replace(
                    events.BEFORE, events.ABORT)
                self._notify_loop(resource, abort_event, trigger, **kwargs)

                raise exceptions.CallbackFailure(errors=errors)
```

调用 `_notify_loop`，并处理其返回的错误。

## `def _get_id(callback)`

```
def _get_id(callback):
    """Return a unique identifier for the callback."""
    # TODO(armax): consider using something other than names
    # https://www.python.org/dev/peps/pep-3155/, but this
    # might be okay for now.
    parts = (reflection.get_callable_name(callback),
             str(hash(callback)))
    return '-'.join(parts)
```

为 `callback` 获取一个独一无二的字符串名称。

# 参考

[Neutron Callback System](https://docs.openstack.org/developer/neutron-lib/devref/callbacks.html)