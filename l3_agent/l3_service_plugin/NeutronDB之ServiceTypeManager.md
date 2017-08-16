# Neutron DB 之 `ServiceTypeManager`

*neutron/db/servicetype_db.py*

## `class ServiceTypeManager(object)`

```
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.config = {}
```

* `get_instance` 方法用于获取该类的实例，若是一直调用此方法，则保证该类的实例只会有一个。

### `def add_provider_configuration(self, service_type, configuration)`

```
    def add_provider_configuration(self, service_type, configuration):
        """Add or update the provider configuration for the service type."""
        LOG.debug('Adding provider configuration for service %s', service_type)
        self.config.update({service_type: configuration})
```

增加一个配置的记录信息

### `def get_service_providers(self, context, filters=None, fields=None)`

根据过滤条件获取 service_provider

### `def get_default_service_provider(self, context, service_type)`

获取某个 service_type 的默认 provider

### `def get_provider_names_by_resource_ids(self, context, resource_ids)`

查询数据库 `ProviderResourceAssociation` 根据 resource_id 获取其对应的 provider name

### `def add_resource_association(self, context, service_type, provider_name, resource_id)`

1. 调用 `get_service_providers` 获取对应的 service provider
2. 若存在该 provier 则在数据库 `ProviderResourceAssociation` 增加一个记录

### `def del_resource_associations(self, context, resource_ids)`

删除数据库 `ProviderResourceAssociation` 中关于 resource_ids 的记录

## 相关数据库

```
class ProviderResourceAssociation(model_base.BASEV2):
    provider_name = sa.Column(sa.String(attr.NAME_MAX_LEN),
                              nullable=False, primary_key=True)
    # should be manually deleted on resource deletion
    resource_id = sa.Column(sa.String(36), nullable=False, primary_key=True,
                            unique=True)
```