# Nutron Ml2 Extension Driver 之 port_security

*neutron/plugins/ml2/extensions/port_security.py*

## `class PortSecurityExtensionDriver(api.ExtensionDriver, ps_db_common.PortSecurityDbCommon, common_db_mixin.CommonDbMixin)`

1. `ExtensionDriver` 为抽象基类，在 *neutron/plugins/ml2/driver_api.py* 中定义，定义了 extension driver 基本的方法（全是 pass，在子类中可以重写）
2. `PortSecurityDbCommon` 我们在本文的下面会介绍
3. `CommonDbMixin` 是关于数据库操作的公共方法的集合，我之前有文章介绍过

`_supported_extension_alias = 'port-security'`

### `def initialize(self)`

```
    def initialize(self):                                                                                                                                              
        LOG.info(_LI("PortSecurityExtensionDriver initialization complete"))
```

无任何操作

### `def extension_alias(self)`

属性方法。

```
    @property
    def extension_alias(self):
        return self._supported_extension_alias
```

### `def extend_network_dict(self, session, db_data, result)`

```
    def extend_network_dict(self, session, db_data, result):                                                                                                           
        self._extend_port_security_dict(result, db_data)
```

`_extend_port_security_dict` 是在 `PortSecurityDbCommon` 中实现的

### `def extend_port_dict(self, session, db_data, result)`

```
    def extend_port_dict(self, session, db_data, result):                                                                                                              
        self._extend_port_security_dict(result, db_data)
```
















## `class PortSecurityDbCommon(object):`

### `def _extend_port_security_dict(self, response_data, db_data)`

```
    def _extend_port_security_dict(self, response_data, db_data):
        if db_data.get('port_security') is None:
            response_data[psec.PORTSECURITY] = psec.DEFAULT_PORT_SECURITY
        else:
            response_data[psec.PORTSECURITY] = ( 
                                db_data['port_security'][psec.PORTSECURITY])
```

* 从这里可以知道，默认的 `port_security` 是为 True 的，我们做个试验，来让它为 False

```
neutron net-create simple --port_security_enabled False
```