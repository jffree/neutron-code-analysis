# Neutron Service plugin router 之 ServicePluginBase

*neutron/services/service_base.py*

## `class ServicePluginBase(extensions.PluginInterface, neutron_worker.WorkerSupportServiceMixin)`

*定义了 service plugin 的框架*

```
@six.add_metaclass(abc.ABCMeta)
class ServicePluginBase(extensions.PluginInterface,
                        neutron_worker.WorkerSupportServiceMixin):
    """Define base interface for any Advanced Service plugin."""
    supported_extension_aliases = []

    @abc.abstractmethod
    def get_plugin_type(self):
        """Return one of predefined service types.

        See neutron/plugins/common/constants.py
        """
        pass

    @abc.abstractmethod
    def get_plugin_description(self):
        """Return string description of the plugin."""
        pass
```

## `class PluginInterface(object)`

*neutron/api/extensions.py*

*不太明白这个是做什么用的。*

```
@six.add_metaclass(abc.ABCMeta)
class PluginInterface(object):

    @classmethod
    def __subclasshook__(cls, klass):
        """Checking plugin class.

        The __subclasshook__ method is a class method
        that will be called every time a class is tested
        using issubclass(klass, PluginInterface).
        In that case, it will check that every method
        marked with the abstractmethod decorator is
        provided by the plugin class.
        """

        if not cls.__abstractmethods__:
            return NotImplemented

        for method in cls.__abstractmethods__:
            if any(method in base.__dict__ for base in klass.__mro__):
                continue
            return NotImplemented
        return True
```

## `class WorkerSupportServiceMixin(object)`

*neutron/worker.py*

简单的框架

```
class WorkerSupportServiceMixin(object):

    @property
    def _workers(self):
        try:
            return self.__workers
        except AttributeError:
            self.__workers = []
        return self.__workers

    def get_workers(self):
        """Returns a collection NeutronWorker instances needed by this service
        """
        return list(self._workers)

    def add_worker(self, worker):
        """Adds NeutronWorker needed for this service

        If a object needs to define workers thread/processes outside of API/RPC
        workers then it will call this method to register worker. Should be
        called on initialization stage before running services
        """
        self._workers.append(worker)

    def add_workers(self, workers):
        """Adds NeutronWorker list needed for this service

        The same as add_worker but adds a list of workers
        """
        self._workers.extend(workers)
```


























