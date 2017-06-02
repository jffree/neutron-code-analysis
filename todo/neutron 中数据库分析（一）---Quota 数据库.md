# neutron 中数据库分析（一）---数据库基础

## 与 quota 相关的 ORM 类

*neutron/db/quota/models.py*

### 


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




















