# Neutron ML2 基类 NeutronDbPluginV2

*neutron/db/db_base_plugin_v2.py*

```
class NeutronDbPluginV2(db_base_plugin_common.DbBasePluginCommon,
                        neutron_plugin_base_v2.NeutronPluginBaseV2,
                        rbac_mixin.RbacPluginMixin,
                        stattr_db.StandardAttrDescriptionMixin)
```

* `DbBasePluginCommon` ml2 的公共方法类
* `NeutronPluginBaseV2` 定义 ml2 plugin 的抽象类
* `RbacPluginMixin` rbac 的 WSGI 实现类
* `StandardAttrDescriptionMixin` **待研究**

这个类实现了 ML2 所需要的大部分公共，其子类 `Ml2Plugin` 也是在此基础上提供其他一些 extension 的功能。

## 类属性

```
    __native_bulk_support = True
    __native_pagination_support = True
    __native_sorting_support = True
```

这表明支持批量、分页、排序操作。

## `def __init__(self)`

1. 定义 ipam 后端（关于ipam，请参考我写的 **Neutron 之 IPAM**）
2. 若在配置文件中设置了 `notify_nova_on_port_status_changes`，则会监听几个数据库事件：
 1. models_v2.Port, 'after_insert', self.nova_notifier.send_port_status
 2. models_v2.Port, 'after_update', self.nova_notifier.send_port_status
 3. models_v2.Port.status, 'set', self.nova_notifier.record_port_status_changed
3. 订阅 rabc 事件
 1. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_CREATE
 2. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_UPDATE
 3. self.validate_network_rbac_policy_change,rbac_mixin.RBAC_POLICY, events.BEFORE_DELETE




























