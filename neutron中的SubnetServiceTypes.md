# Neutron 之 SubnetServiceTypes


## extensions

*neutron/extensions/subnet_service_types.py*

`class Subnet_service_types(extensions.ExtensionDescriptor)`

## Model

*neutron/db/subnet_service_type.py*

`class SubnetServiceType(model_base.BASEV2)`

## WSGI 

*neutron/db/subnet_service_type_db_models.py*

## `class SubnetServiceTypeMixin(object)`

```
    common_db_mixin.CommonDbMixin.register_dict_extend_funcs(
        attributes.SUBNETS, [_extend_subnet_service_types])
```

### `def _extend_subnet_service_types(self, subnet_res, subnet_db)`

```
    def _extend_subnet_service_types(self, subnet_res, subnet_db):
        subnet_res['service_types'] = [service_type['service_type'] for
                                       service_type in
                                       subnet_db.service_types]
```