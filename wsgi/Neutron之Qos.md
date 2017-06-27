# Neutron 之 Qos

关于 Qos 的介绍和配置，请参考：

[Quality of Service (QoS)](https://docs.openstack.org/mitaka/networking-guide/config-qos.html)

* extension：*neutron/extensions/qos.py*
* WSGI：*neutron/services/qos/qos_plugin.py*（从这里我们看出 qos 是以 service plugin 的形式实现的）
* Model：*neutron/db/qos/models.py*

extension 我们就略过了，架构都是一样的。

我们看 WSGI 的实现：

## `class QoSPluginBase(service_base.ServicePluginBase)`

### 类属性

```
    path_prefix = QOS_PREFIX

    # The rule object type to use for each incoming rule-related request.
    rule_objects = {'bandwidth_limit': rule_object.QosBandwidthLimitRule,
                    'dscp_marking': rule_object.QosDscpMarkingRule,
                    'minimum_bandwidth': rule_object.QosMinimumBandwidthRule}

    # Patterns used to call method proxies for all policy-rule-specific
    # method calls (see __getattr__ docstring, below).
    qos_rule_method_patterns = [
            re.compile(
                r"^((create|update|delete)_policy_(?P<rule_type>.*)_rule)$"),
            re.compile(
                r"^(get_policy_(?P<rule_type>.*)_(rules|rule))$"),
                               ]
```

### `def __getattr__(self, attrib)`

### `def _call_proxy_method(self, method_name, rule_cls)`

**`__getattr__` 和 `_call_proxy_method` 方法共同的实现了下面的目的：**

将 WSGI 的请求方法（例如：`get_policy_dscp_marking_rule`），转化为类 （`QoSPlugin`）方法（`get_policy_rule`）。

```
`get_policy_dscp_marking_rule` --->  `get_policy_rule`
```

## `class QoSPlugin(qos.QoSPluginBase)`

`qos.QoSPluginBase` 是在 extension 中定义的抽象基类。这个类实现了 [`qos` WSGI](https://developer.openstack.org/api-ref/networking/v2/index.html?expanded=#quality-of-service) 的所有操作。

```
    supported_extension_aliases = ['qos']
 
    __native_pagination_support = True
    __native_sorting_support = True
```

### `def __init__(self)`

```
    def __init__(self):                                                                                                                                                
        super(QoSPlugin, self).__init__()
        self.notification_driver_manager = (
            driver_mgr.QosServiceNotificationDriverManager())
```

创建了一个 rpc 的通知驱动管理器的实例，默认的 driver 为 `message_queue`（可以看一下 qos 配置的加载方法：*neutron/conf/services/qos_driver_manager.py* 的 `register_qos_plugin_opts`。）。

我们看在 setup.cfg 中：

```
neutron.qos.notification_drivers =
    message_queue = neutron.services.qos.notification_drivers.message_queue:RpcQosServiceNotificationDriver
```

关于通知驱动管理器我们会在下面介绍。

### `def create_policy(self, context, policy)`

创建一个 `QosPolicy` 对象 `policy_obj`，调用该对象的 `create` 方法。

发送通知。

### `def update_policy(self, context, policy_id, policy)`

同样通过创建 `QosPolicy` 对象来实现。

### `def delete_policy(self, context, policy_id)`

通过创建 `QosPolicy` 对象来实现。

### `def get_policy(self, context, policy_id, fields=None)`

### `def _get_policy_obj(self, context, policy_id)`

通过创建 `QosPolicy` 对象来实现。

### `def get_policies(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/qos/policies -H 'Content-Type: application/json' -H 'X-Auth-Token: 2d26251fb22f40d88d72be12d38d96d1'
```

通过创建 `QosPolicy` 对象来实现。

### `def get_rule_types(self, context, filters=None, fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

测试方法：

```
curl -s -X GET http://172.16.100.106:9696//v2.0/qos/rule-types -H 'Content-Type: application/json' -H 'X-Auth-Token: 2d26251fb22f40d88d72be12d38d96d1'
```

通过创建 `QosPolicy` 对象来实现。

### `def create_policy_rule(self, context, rule_cls, policy_id, rule_data)`

通过创建 `QosPolicy` 对象和创建 `rule` 对象（有三种）联合实现。

### `def update_policy_rule(self, context, rule_cls, rule_id, policy_id, rule_data)`

通过创建 `QosPolicy` 对象和创建 `rule` 对象（有三种）联合实现。

### `def get_policy_rule(self, context, rule_cls, rule_id, policy_id, fields=None)`

通过创建 `QosPolicy` 对象和创建 `rule` 对象（有三种）联合实现。

### `def get_policy_rules(self, context, rule_cls, policy_id, filters=None,  fields=None, sorts=None, limit=None, marker=None, page_reverse=False)`

通过创建 `QosPolicy` 对象和创建 `rule` 对象（有三种）联合实现。