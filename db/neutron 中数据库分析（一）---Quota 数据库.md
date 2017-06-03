# neutron 中数据库分析（一）--- Quota 相关的数据库

## 与 Quota 数据库相关的 ORM 类

* *neutron/db/quota/models.py*

### `Quota` 模型

```
class Quota(model_base.BASEV2, model_base.HasId, model_base.HasProject):
    """Represent a single quota override for a tenant.

    If there is no row for a given tenant id and resource, then the
    default for the deployment is used.
    """
    resource = sa.Column(sa.String(255))
    limit = sa.Column(sa.Integer)
```

* 在 neutron 中， Quota 的配置信息存在于两个地方：
 1. 第一个是默认的配置，保存于 Quota 对待追踪资源的封装类中：（`BaseResource` 的子类）。默认的配置信息是从 `conf`（配置信息）中获取，`BaseResource` 中的 `flag` 标志就是用来获取该资源 Quota 配置的。
 2. 第二个保存于名为 `quotas` 的数据库中，当用户修改过某一资源的 Quota 配置时，这些配置就会保存于 `quotas` 的数据库中。

在获取某一资源的 Quota 配置信息的时候，会首先获取其默认配置，然后再从数据库中更新默认配置。

### `QuotaUsage` 模型

```
class QuotaUsage(model_base.BASEV2, model_base.HasProjectPrimaryKeyIndex):
    """Represents the current usage for a given resource."""

    resource = sa.Column(sa.String(255), nullable=False,
                         primary_key=True, index=True)
    dirty = sa.Column(sa.Boolean, nullable=False, server_default=sql.false())

    in_use = sa.Column(sa.Integer, nullable=False,
                       server_default="0")
    reserved = sa.Column(sa.Integer, nullable=False,
                         server_default="0")
```

用于存储某一项目下，某一资源的使用情况。

`dirty` 字段：`dirty` 位表示该资源的数据库发生了插入或者删除操作；

在 `dirty` 字段被置位（`True`）后，会在计数（count）操作用更新 `in_use` 字段（表示目前实际的资源使用量）

### `ResourceDelta` 与 `Reservation`

```
class ResourceDelta(model_base.BASEV2):
    resource = sa.Column(sa.String(255), primary_key=True)
     = sa.Column(sa.String(36),
                               sa.ForeignKey('reservations.id',
                                             ondelete='CASCADE'),
                               primary_key=True,
                               nullable=False)
    # Requested amount of resource
    amount = sa.Column(sa.Integer)


class Reservation(model_base.BASEV2, model_base.HasId,
                  model_base.HasProjectNoIndex):
    expiration = sa.Column(sa.DateTime())
    resource_deltas = orm.relationship(ResourceDelta,
                                       backref='reservation',
                                       lazy="joined",
                                       cascade='all, delete-orphan')
```

`ResourceDelta` 与 `Reservation` 是多对一的关系，且当 `Reservation` 的一列被删除时，与之对应的 `ResourceDelta` 多列都会被删除。

这两个数据模型用于表示资源预留的情况。

* `expiration` 此次预留的有效时间
* `resource` 资源名称
* `amount` 预留的数量

当资源（比如说 network）创建时，有可能会有多个请求同时发过来，这时针对每个请求会先进行一个创建预留资源的操作（应该是有的资源创建比较费时间的原因吧），若有效期内的预留数量加上已经使用的资源数量不满足请求创建的资源数量，则无法创建资源。

这个预留是有有效期的，超过有效期的会被删除。

## `BASEV2`

*neutron_lib/db/model_base.py*

```
class NeutronBaseV2(_NeutronBase):

    @declarative.declared_attr
    def __tablename__(cls):
        # Use the pluralized name of the class as the table name.
        return cls.__name__.lower() + 's'


BASEV2 = declarative.declarative_base(cls=NeutronBaseV2)
```

`BASEV2` 为继承于 `NeutronBaseV2`  ORM 基类
