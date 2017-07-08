# Neutron 之 ServiceType

## extensions

*neutron/extensions/servicetype.py*

`class Servicetype(extensions.ExtensionDescriptor)`

## WSGI and Model

Model : `class ProviderResourceAssociation(model_base.BASEV2)`

## `class ServiceTypeManager(object)`

### `def get_instance(cls)`

类方法，通过该方法获取 `ServiceTypeManager` 的全局唯一实例

### `def __init__(self)`

```
    def __init__(self):
        self.config = {}
```

### `def add_provider_configuration(self, service_type, configuration)`

增加或者更新 self.config

```
    def add_provider_configuration(self, service_type, configuration):
        """Add or update the provider configuration for the service type."""
        LOG.debug('Adding provider configuration for service %s', service_type)
        self.config.update({service_type: configuration})
```

### `def get_service_providers(self, context, filters=None, fields=None)`

从 self.config 中的每个配置中读取他们的所有的 provider

### `def get_default_service_provider(self, context, service_type)`

获取某种 service_type 中默认的 provider

### `def get_provider_names_by_resource_ids(self, context, resource_ids)`

通过 resource_id 读取 `ProviderResourceAssociation` 数据库中对应的 provider_name

### `def add_resource_association(self, context, service_type, provider_name, resource_id)`

1. 调用 `get_service_providers` 根据 service_type 和 provider_name 获取对应的 provider
2. 若是获取成功则表示该 provider 存在，则进一步创建 `ProviderResourceAssociation` 的数据库记录

### `def del_resource_associations(self, context, resource_ids)`

根据 resource_ids 删除 `ProviderResourceAssociation` 的数据库记录


## service

*neutron/services/provider_configuration.py*

## `class ProviderConfiguration(object)`











