# Neutron Services 之 Segments

## extension

*neutron/extensions/segment.py*

## WSGI 实现

*neutron/services/segments/plugin.py*

*neutron/services/segments/db.py*

`class Plugin(db.SegmentDbMixin, segment.SegmentPluginBase)`

`class SegmentDbMixin(common_db_mixin.CommonDbMixin)`

## Model

*neutron/services/segments/db.py*

`class SegmentHostMapping(model_base.BASEV2)`

*neutron/db/segments_db.py*

`class NetworkSegment(standard_attr.HasStandardAttributes, model_base.BASEV2, model_base.HasId)`

## 开启 Segments 服务

```
vim /etc/neutron/neutron.conf
```

*在 service_plugins 中增加 segments。*

```
service_plugins = neutron.services.l3_router.l3_router_plugin.L3RouterPlugin, segments
```