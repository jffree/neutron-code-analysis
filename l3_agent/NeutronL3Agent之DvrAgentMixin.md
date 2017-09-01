# Neutron L3 Agent 之 Ha AgentMixin

*neutron/agent/l3/dvr.py*

## `class AgentMixin(object)`

```
class AgentMixin(object):
    def __init__(self, host):
        # dvr data
        self._fip_namespaces = weakref.WeakValueDictionary()
        super(AgentMixin, self).__init__(host)
```
