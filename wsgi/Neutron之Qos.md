# Neutron 之 Qos

关于 Qos 的介绍和配置，请参考：

[Quality of Service (QoS)](https://docs.openstack.org/mitaka/networking-guide/config-qos.html)

* extension：*neutron/extensions/qos.py*
* WSGI：*neutron/services/qos/qos_plugin.py*（从这里我们看出 qos 是以 service plugin 的形式实现的）
* Model：*neutron/db/qos/models.py*

extension 我们就略过了，架构都是一样的。

我们看 WSGI 的实现：

## `class QoSPlugin(qos.QoSPluginBase)`

`qos.QoSPluginBase` 是在 extension 中定义的抽象基类。

```
    supported_extension_aliases = ['qos']
 
    __native_pagination_support = True
    __native_sorting_support = True
```

### `def __init__(self)`



























