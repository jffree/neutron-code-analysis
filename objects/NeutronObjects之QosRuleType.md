# Neutron objects 之 QosRuleType

```
class RuleTypeField(obj_fields.BaseEnumField):

    def __init__(self, **kwargs):
        self.AUTO_TYPE = obj_fields.Enum(
            valid_values=qos_consts.VALID_RULE_TYPES)
        super(RuleTypeField, self).__init__(**kwargs)
```

```
@obj_base.VersionedObjectRegistry.register
class QosRuleType(base.NeutronObject):
    # Version 1.0: Initial version
    # Version 1.1: Added QosDscpMarkingRule
    # Version 1.2: Added QosMinimumBandwidthRule
    VERSION = '1.2'

    fields = {
        'type': RuleTypeField(),
    }

    # we don't receive context because we don't need db access at all
    @classmethod
    def get_objects(cls, validate_filters=True, **kwargs):
        if validate_filters:
            cls.validate_filters(**kwargs)
        core_plugin = manager.NeutronManager.get_plugin()
        # TODO(ihrachys): apply filters to returned result
        return [cls(type=type_)
                for type_ in core_plugin.supported_qos_rule_types]
```

当我们 WSGI 访问 `/v2.0/qos/rule-types` 就是调用 `get_objects` 方法实现的。