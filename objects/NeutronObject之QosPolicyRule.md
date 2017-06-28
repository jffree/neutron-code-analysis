# Neutron objcet 之 Qos Rule

*neutron/objects/qos/rule.py*

qos policy 一共有三种形式的 rule，分别是：`bandwidth_limit`、`dscp_marking`、`minimum_bandwidth`

这个模块就是针对这三中 rule 设计了三种 object

## `def get_rules(context, qos_policy_id)`

获取该 qos policy 所拥有的所有 rule。

## `class QosRule(base.NeutronDbObject)`

抽象基类。

### 类属性

```
    VERSION = '1.2'

    fields = {
        'id': obj_fields.UUIDField(),
        'qos_policy_id': obj_fields.UUIDField()
    }

    fields_no_update = ['id', 'qos_policy_id']

    # should be redefined in subclasses
    rule_type = None
```

### `def to_dict(self)`

为 rule objcet 增加 `type` 属性

### `def should_apply_to_port(self, port)`

判断该 rule 是否可以加载到 port 资源上。

## `class QosBandwidthLimitRule(QosRule)`

```
@obj_base.VersionedObjectRegistry.register
class QosBandwidthLimitRule(QosRule):

    db_model = qos_db_model.QosBandwidthLimitRule

    fields = {
        'max_kbps': obj_fields.IntegerField(nullable=True),
        'max_burst_kbps': obj_fields.IntegerField(nullable=True)
    }

    rule_type = qos_consts.RULE_TYPE_BANDWIDTH_LIMIT
```

## `class QosDscpMarkingRule(QosRule)`

```
@obj_base.VersionedObjectRegistry.register
class QosDscpMarkingRule(QosRule):

    db_model = qos_db_model.QosDscpMarkingRule

    fields = {
        DSCP_MARK: common_types.DscpMarkField(),
    }

    rule_type = qos_consts.RULE_TYPE_DSCP_MARKING

    def obj_make_compatible(self, primitive, target_version):
        _target_version = versionutils.convert_version_to_tuple(target_version)
        if _target_version < (1, 1):
            raise exception.IncompatibleObjectVersion(
                                 objver=target_version,
                                 objname="QosDscpMarkingRule")
```


## `class QosMinimumBandwidthRule(QosRule)`

```
@obj_base.VersionedObjectRegistry.register
class QosMinimumBandwidthRule(QosRule):

    db_model = qos_db_model.QosMinimumBandwidthRule

    fields = {
        'min_kbps': obj_fields.IntegerField(nullable=True),
        'direction': common_types.FlowDirectionEnumField(),
    }

    rule_type = qos_consts.RULE_TYPE_MINIMUM_BANDWIDTH

    def obj_make_compatible(self, primitive, target_version):
        _target_version = versionutils.convert_version_to_tuple(target_version)
        if _target_version < (1, 2):
            raise exception.IncompatibleObjectVersion(
                                 objver=target_version,
                                 objname="QosMinimumBandwidthRule")
```



