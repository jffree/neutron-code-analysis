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

### `def process_create_network(self, context, data, result)`

```
    def process_create_network(self, context, data, result):                                                                                                           
        # Create the network extension attributes.
        if psec.PORTSECURITY not in data:
            data[psec.PORTSECURITY] = psec.DEFAULT_PORT_SECURITY
        self._process_network_port_security_create(context, data, result)
```

* 调用 `_process_network_port_security_create` 做实际的处理（`PortSecurityDbCommon` 实现）

### `def process_update_network(self, context, data, result)`

```
    def process_update_network(self, context, data, result):                                                                                                           
        # Update the network extension attributes.
        if psec.PORTSECURITY in data:
            self._process_network_port_security_update(context, data, result)
```

* 调用 `_process_network_port_security_create` 做实际的处理（`PortSecurityDbCommon` 实现）

### `def process_create_port(self, context, data, result)`

```
    def process_create_port(self, context, data, result):
        # Create the port extension attributes.
        data[psec.PORTSECURITY] = self._determine_port_security(context, data)
        self._process_port_port_security_create(context, data, result)
```

1. 首先调用 `_determine_port_security` 来确定该 port 数据的 `port_security_enabled` 属性值（True or False）
2. 再调用 `_process_port_port_security_create` 做实际的处理（`PortSecurityDbCommon` 实现）

### `def process_update_port(self, context, data, result)`

```
    def process_update_port(self, context, data, result):
        if psec.PORTSECURITY in data:                                                                                                                                  
            self._process_port_port_security_update(
                context, data, result)
```

* 调用 `_process_port_port_security_create` 做实际的处理（`PortSecurityDbCommon` 实现）

### `def _determine_port_security(self, context, port)`

1. 对于网络内部的端口（通过 `utils.is_port_trusted`来判断）是不应用 prot security 的（对于其他端口，比如说虚拟机的网卡，device_owner 为 compute:nova，就回应用 port security）。
2. 若欲创建的 port 资源的数据中包含 `port_security_enabled` 则使用这个属性的数据
3. 若欲创建的 port 资源的数据中不包含 `port_security_enabled` 则调用 `_get_network_security_binding` 这个方法获取

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

### `def _get_port_security_binding(self, context, port_id)`

```
    def _get_port_security_binding(self, context, port_id):                                                                                                            
        return self._get_security_binding(context, p_ps.PortSecurity, port_id)
```

### `def _get_network_security_binding(self, context, network_id)`

```
    def _get_network_security_binding(self, context, network_id):                                                                                                      
        return self._get_security_binding(
            context, n_ps.NetworkPortSecurity, network_id)
```

### `def _get_security_binding(self, context, obj_cls, res_id)`

```
    def _get_security_binding(self, context, obj_cls, res_id):                                                                                                         
        obj = obj_cls.get_object(context, id=res_id)
        # NOTE(ihrachys) the resource may have been created before port
        # security extension was enabled; return default value
        return obj.port_security_enabled if obj else psec.DEFAULT_PORT_SECURITY
```

通过 `NetworkPortSecurity` 或 `PortSecurity` object 来获取该 object 的 `port_security_enabled` 的属性。若是没有获取该对象，则默认为 True。

### `def _process_network_port_security_create(self, context, network_req, network_res)`

```
    def _process_network_port_security_create(
        self, context, network_req, network_res):                                                                                                                      
        self._process_port_security_create(
            context, n_ps.NetworkPortSecurity, 'network',
            network_req, network_res)
```

* 调用 `_process_port_security_create` 实现

### `def _process_port_port_security_create(self, context, port_req, port_res)`

```
    def _process_port_port_security_create(
        self, context, port_req, port_res):
        self._process_port_security_create(
            context, p_ps.PortSecurity, 'port',
            port_req, port_res)
```

* 调用 `_process_port_security_create` 实现

### `def _process_port_security_create(self, context, obj_cls, res_name, req, res)`

1. 通过调用 `PortSecurity` 或者 `NetworkPortSecurity` object 来实现相应数据库的创建
2. 调用 `_make_port_security_dict` 返回创建的结果

### `def _make_port_security_dict(self, res, res_name, fields=None)`

```
    def _make_port_security_dict(self, res, res_name, fields=None):
        res_ = {'%s_id' % res_name: res.id,
                psec.PORTSECURITY: res.port_security_enabled}
        return self._fields(res_, fields) 
```

`_fields` 方法是在 `CommonDbMixin` 中定义的，为结果增加 `tenant_id` 或者 `project_id` 属性

### `def _process_port_port_security_update(self, context, port_req, port_res)`

```
    def _process_port_port_security_update(                                                                                                                            
        self, context, port_req, port_res):
        self._process_port_security_update(
            context, p_ps.PortSecurity, 'port', port_req, port_res)
```

### `def _process_network_port_security_update`

```
    def _process_network_port_security_update(                                                                                                                         
        self, context, network_req, network_res):
        self._process_port_security_update( 
            context, n_ps.NetworkPortSecurity, 'network',
            network_req, network_res)
```

### `def _process_port_security_update(self, context, obj_cls, res_name, req, res)`

1. 通过调用 `PortSecurity` 或者 `NetworkPortSecurity` object 来实现相应数据库的更新。
2. 若是该 object 不存在，则调用 `_process_port_security_create` 进行创建（object 和 数据库记录）