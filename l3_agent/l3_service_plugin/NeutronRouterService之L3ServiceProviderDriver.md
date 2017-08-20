# Neutron Router Service 之 L3Service Provider Driver

provider driver 是定义了对 dvr、dvrha、ha、single_node 模式的支持情况

这些实现都位于 *neutron/services/l3_router/service_providers 下*

## 辅助类：`class _FeatureFlag(object)`

```
class _FeatureFlag(object):

    def is_compatible(self, value):
        if value == self.requires:
            return True
        if value and self.supports:
            return True
        return False

    def __init__(self, supports, requires):
        self.supports = supports
        self.requires = requires
        if requires and not supports:
            raise RuntimeError(_("A driver can't require a feature and not "
                                 "support it."))

UNSUPPORTED = _FeatureFlag(supports=False, requires=False)
OPTIONAL = _FeatureFlag(supports=True, requires=False)
MANDATORY = _FeatureFlag(supports=True, requires=True)
```

## 基类：`class L3ServiceProvider(object)`

```
class L3ServiceProvider(object):
    """Base class for L3 service provider drivers.

    On __init__ this will be given a handle to the l3 plugin. It is then the
    responsibility of the driver to subscribe to the events it is interested
    in (e.g. router_create, router_update, router_delete, etc).

    The 'ha' and 'distributed' attributes below are used to determine if a
    router request with the 'ha' or 'distributed' attribute can be supported
    by this particular driver. These attributes must be present.

    The 'use_integrated_agent_scheduler' flag indicates whether or not routers
    which belong to the driver should be automatically scheduled using the L3
    agent scheduler integrated into Neutron.
    """

    ha_support = UNSUPPORTED
    distributed_support = UNSUPPORTED
    use_integrated_agent_scheduler = False

    def __init__(self, l3plugin):
        self.l3plugin = l3plugin
```

一个继承自 `L3ServiceProvider` 的 support driver 表明该 router 是否支持 ha 模式、是否支持 distributed 模式、是否支持调度。

## `class SingleNodeDriver(base.L3ServiceProvider)`

```
class SingleNodeDriver(base.L3ServiceProvider):
    """Provider for single L3 agent routers."""
    use_integrated_agent_scheduler = True
```

仅支持 l3 agent 的调度

## `class HaDriver(base.L3ServiceProvider)`

```
class HaDriver(base.L3ServiceProvider):
    ha_support = base.MANDATORY
    use_integrated_agent_scheduler = True
```

需要 ha 模式，同时支持 ha 模式

支持 l3 agent 的调度

## `class DvrDriver(base.L3ServiceProvider)`

```
class DvrDriver(base.L3ServiceProvider):
    distributed_support = base.MANDATORY
    use_integrated_agent_scheduler = True
```

需要 distributed 并且支持 distributed 模式

支持 l3 agent 的调度

## `class DvrHaDriver(dvr.DvrDriver, ha.HaDriver)`

```
class DvrHaDriver(dvr.DvrDriver, ha.HaDriver):
    ha_support = base.MANDATORY
    dvr_support = base.MANDATORY
```

同时需要 ha 和 distributed 模式，也同时支持这两种模式

支持 l3 agent 的调度