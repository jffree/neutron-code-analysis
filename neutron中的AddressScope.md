# Neutron 之 AddressScope

## 测试

```
neutron address-scope-create --shared test 4
Created a new address_scope:
+------------+--------------------------------------+
| Field      | Value                                |
+------------+--------------------------------------+
| id         | 6ed242e0-13c9-4dfb-a455-bf63436d47c0 |
| ip_version | 4                                    |
| name       | test                                 |
| project_id | d4edcc21aaca452dbc79e7a6056e53bb     |
| shared     | True                                 |
| tenant_id  | d4edcc21aaca452dbc79e7a6056e53bb     |
+------------+--------------------------------------+
```


## extensions

*neutron/extensions/address_scope.py*

`class Address_scope(extensions.ExtensionDescriptor)`

`class AddressScopePluginBase(object)`

## WSGI 实现

*neutron/db/address_scope_db.py*

`class AddressScopeDbMixin(ext_address_scope.AddressScopePluginBase)`

## Model

*neutron/db/models/address_scope.py*

`class AddressScope(model_base.BASEV2, model_base.HasId, model_base.HasProject)`

























