# Neutron Service Plugin 之 `ProviderConfiguration`

*neutron/services/provider_configuration.py*

## `class ProviderConfiguration(object)`

```
    def __init__(self, svc_module='neutron'):
        self.providers = {}
        for prov in parse_service_provider_opt(svc_module):
            self.add_provider(prov)
```

调用 `parse_service_provider_opt` 读取配置文件中关于 `service_providers.service_provider` 的设定

### `def _ensure_driver_unique(self, driver)`

确保在所有的 provider 中 driver 是唯一的

### `def _ensure_default_unique(self, type, default)`

确保默认的 provider 是唯一的

### `def add_provider(self, provider)`

增加一个 provider 记录（参考 `_LegacyPlusProviderConfiguration.__init__` 方法）

### `def _check_entry(self, k, v, filters)`

根据 filter 检查 k v 是否符合过滤条件

### `def _fields(self, resource, fields)`

fields 用来 resource 中感兴趣的数据

### `def get_service_providers(self, filters=None, fields=None)`

获取符合 filters 的 providers 数据


## `def parse_service_provider_opt(service_module='neutron')`

1. 构建一个 `NeutronModule` 对象
2. 调用 `NeutronModule.service_providers` 来获取关于 `service_providers.service_provider` 的配置

## `class NeutronModule(object)`

```
    def __init__(self, service_module):
        self.module_name = service_module
        self.repo = {
            'mod': self._import_or_none(),
            'ini': None
        }
```

调用 `_import_or_none` 导入名为 service_module 的 python module

### `def _import_or_none(self)`

```
    def _import_or_none(self):
            try:
                return importlib.import_module(self.module_name)
            except ImportError:
                return None
```

### `def installed(self)`

```
    def installed(self):
        LOG.debug("NeutronModule installed = %s", self.module_name)
        return self.module_name
```

### `def module(self)`

```
    def module(self):
        return self.repo['mod']
```

### `def ini(self, neutron_dir=None)`

找到 neutron 的配置文件 */etc/neutron/neutron.conf* 中，并读取其中的配置，并将其放到 `ini` 中。


### `def service_providers(self)`

1. 获取对 `service_providers.service_provider` 的设定
2. 若没有设定 `service_providers.service_provider`，则调用 `ini`，通过读取配置文件中的设定来获取 `service_provider`


## `class _LegacyPlusProviderConfiguration(provider_configuration.ProviderConfiguration)`

```
    def __init__(self):
        # loads up ha, dvr, and single_node service providers automatically.
        # If an operator has setup explicit values that conflict with these,
        # the operator defined values will take priority.
        super(_LegacyPlusProviderConfiguration, self).__init__()
        for name, driver in (('dvrha', 'dvrha.DvrHaDriver'),
                             ('dvr', 'dvr.DvrDriver'), ('ha', 'ha.HaDriver'),
                             ('single_node', 'single_node.SingleNodeDriver')):
            path = 'neutron.services.l3_router.service_providers.%s' % driver
            try:
                self.add_provider({'service_type': constants.L3_ROUTER_NAT,
                                   'name': name, 'driver': path,
                                   'default': False})
            except lib_exc.Invalid:
                LOG.debug("Could not add L3 provider '%s', it may have "
                          "already been explicitly defined.", name)
```






