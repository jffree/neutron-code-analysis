# Neutron Ml2 之 ExtraDhcpOpt

## extensions

*neutron/extensions/extra_dhcp_opt.py*

`class Extra_dhcp_opt(extensions.ExtensionDescriptor)`

## Model

*neutron/db/extra_dhcp_opt/models.py*

`class ExtraDhcpOpt(model_base.BASEV2, model_base.HasId)`

## object

*neutron/objects/port/extensions/extra_dhcp_opt.py*

`class ExtraDhcpOpt(base.NeutronDbObject)`

## WSGI

*neutron/db/extradhcpopt_db.py*

## `class ExtraDhcpOptMixin(object)`

```
    def _extend_port_dict_extra_dhcp_opt(self, res, port):
        res[edo_ext.EXTRADHCPOPTS] = [{'opt_name': dho.opt_name,
                                       'opt_value': dho.opt_value,
                                       'ip_version': dho.ip_version}
                                      for dho in port.dhcp_opts]
        return res

    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attributes.PORTS, ['_extend_port_dict_extra_dhcp_opt'])
```

### `def _is_valid_opt_value(self, opt_name, opt_value)`

检查 `extra_dhcp_opt` 的键值是否合法

### `def _process_port_create_extra_dhcp_opts(self, context, port, extra_dhcp_opts)`

根据 port 的数据，和 extra_dhcp_opts 的信息创建 `ExtraDhcpOpt` 数据库记录

1. 验证 `extra_dhcp_opts` 是否存在
2. 调用 `_is_valid_opt_value` 验证数据是否合法
3. 调用 `obj_extra_dhcp.ExtraDhcpOpt` 创建对象，调用对象的 create 方法创建数据库记录
4. 调用 `_extend_port_extra_dhcp_opts_dict` 返回创建后的易读信息

### `def _extend_port_extra_dhcp_opts_dict(self, context, port)`

```
    def _extend_port_extra_dhcp_opts_dict(self, context, port):
        port[edo_ext.EXTRADHCPOPTS] = self._get_port_extra_dhcp_opts_binding(
            context, port['id'])
```

### `def _get_port_extra_dhcp_opts_binding(self, context, port_id)`

根据 port id 构造 `ExtraDhcpOpt` 对象，通过对象的信息构造易读的数据

### `def _update_extra_dhcp_opts_on_port(self, context, id, port, updated_port=None)`

* `id` ： port 的 id
* `port`：待更新的 port 的数据
* `updated_port`：已经更新过的 port 的数据

1. 构造 `ExtraDhcpOpt` 对象
2. 调用 `_is_valid_opt_value` 验证数据的合法性
3. 利用 `ExtraDhcpOpt` 对象进行数据库的更新或者创建
4. 调用 `_get_port_extra_dhcp_opts_binding` 填充 `updated_port`，使之完善