# neutron 中的 quota

* 资源追踪

```
class tracked_resources(object):
    """Decorator for specifying resources for which usage should be tracked.

    A plugin class can use this decorator to specify for which resources
    usage info should be tracked into an appropriate table rather than being
    explicitly counted.
    """

    def __init__(self, override=False, **kwargs):
        self._tracked_resources = kwargs
        self._override = override

    def __call__(self, f):

        @six.wraps(f)
        def wrapper(*args, **kwargs):
            registry = ResourceRegistry.get_instance()
            for resource_name in self._tracked_resources:
                registry.set_tracked_resource(
                    resource_name,
                    self._tracked_resources[resource_name],
                    self._override)
            return f(*args, **kwargs)

        return wrapper
```

`tracked_resources` 是一个装饰器类，`_tracked_resources` 用于保存需要追踪的资源。

`tracked_resources` 的 `__call__` 既是往 `ResourceRegistry` 的实例中注册待追踪的资源。

`ResourceRegistry` 是一个全局具有唯一实例的类，用于对追踪资源的处理。