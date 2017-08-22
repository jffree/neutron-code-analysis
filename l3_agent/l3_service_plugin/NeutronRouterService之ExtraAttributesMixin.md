# Neutron Router Service 之 ExtraAttributesMixin

*neutron/db/l3_attrs_db.py*

## 数据库 RouterExtraAttributes

```
class RouterExtraAttributes(model_base.BASEV2):
    """Additional attributes for a Virtual Router."""

    # NOTE(armando-migliaccio): this model can be a good place to
    # add extension attributes to a Router model. Each case needs
    # to be individually examined, however 'distributed' and other
    # simple ones fit the pattern well.
    __tablename__ = "router_extra_attributes"
    router_id = sa.Column(sa.String(36),
                          sa.ForeignKey('routers.id', ondelete="CASCADE"),
                          primary_key=True)
    # Whether the router is a legacy (centralized) or a distributed one
    distributed = sa.Column(sa.Boolean, default=False,
                            server_default=sa.sql.false(),
                            nullable=False)
    # Whether the router is to be considered a 'service' router
    service_router = sa.Column(sa.Boolean, default=False,
                               server_default=sa.sql.false(),
                               nullable=False)
    ha = sa.Column(sa.Boolean, default=False,
                   server_default=sa.sql.false(),
                   nullable=False)
    ha_vr_id = sa.Column(sa.Integer())
    # Availability Zone support
    availability_zone_hints = sa.Column(sa.String(255))

    router = orm.relationship(
        'Router',
        backref=orm.backref("extra_attributes", lazy='joined',
                            uselist=False, cascade='delete'))
    revises_on_change = ('router', )
```

## `class ExtraAttributesMixin(object)`

```
    extra_attributes = []

    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        l3.ROUTERS, ['_extend_extra_router_dict'])
```

### `def _extend_extra_router_dict(self, router_res, router_db)`

若 router_db 已经有某种属性（例如 `distributed`）的值，则使用该值；若是没有该属性值，则使用其默认值。

### `def _get_extra_attributes(self, router, extra_attributes)`

返回当前 router 的扩展属性

### `def _process_extra_attr_router_create(self, context, router_db, router_req)`

1. 调用 `_get_extra_attributes` 获取当前 router 的属性
2. 若数据库 `RouterExtraAttributes` 中没有该 router 的记录，则增加记录
3. 若是已经有数据库记录，则更新其中的默认值