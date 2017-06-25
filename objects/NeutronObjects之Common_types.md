# Neutron Object 之 Common_types

*neutron/objects/common_types.py*

这里面定义了 Neutron 中用到的一些 field

## `class IPV6ModeEnumField(obj_fields.AutoTypedField)`

```
class IPV6ModeEnumField(obj_fields.AutoTypedField):
    AUTO_TYPE = obj_fields.Enum(valid_values=lib_constants.IPV6_MODES)
```

## `class RangeConstrainedInteger(obj_fields.Integer)`

一个有前后范围的 Integer field type

```
class RangeConstrainedInteger(obj_fields.Integer):
    def __init__(self, start, end, **kwargs):
        try:
            self._start = int(start)
            self._end = int(end)
        except (TypeError, ValueError):
            raise NeutronRangeConstrainedIntegerInvalidLimit(
                start=start, end=end)
        super(RangeConstrainedInteger, self).__init__(**kwargs)

    def coerce(self, obj, attr, value):
        if not isinstance(value, six.integer_types):
            msg = _("Field value %s is not an integer") % value
            raise ValueError(msg)
        if not self._start <= value <= self._end:
            msg = _("Field value %s is invalid") % value
            raise ValueError(msg)
        return super(RangeConstrainedInteger, self).coerce(obj, attr, value)
```

## `class IPNetworkPrefixLen(RangeConstrainedInteger)` 与 `class IPNetworkPrefixLenField(obj_fields.AutoTypedField)`

```
class IPNetworkPrefixLen(RangeConstrainedInteger):
    """IP network (CIDR) prefix length custom Enum"""
    def __init__(self, **kwargs):
        super(IPNetworkPrefixLen, self).__init__(
              start=0, end=lib_constants.IPv6_BITS,
              **kwargs)

class IPNetworkPrefixLenField(obj_fields.AutoTypedField):
    AUTO_TYPE = IPNetworkPrefixLen()
```

## `class PortRange(RangeConstrainedInteger)` 与 `class PortRangeField(obj_fields.AutoTypedField)`

```
class PortRange(RangeConstrainedInteger):
    def __init__(self, **kwargs):
        super(PortRange, self).__init__(start=constants.PORT_RANGE_MIN,
                                        end=constants.PORT_RANGE_MAX, **kwargs)


class PortRangeField(obj_fields.AutoTypedField):
    AUTO_TYPE = PortRange()
```

#其他

懒了，写了也是 copy 的代码
