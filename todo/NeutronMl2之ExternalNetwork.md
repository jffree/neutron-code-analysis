# Neutron Ml2 之 ExternalNetwork

我们创建 network 的时候，有一个 `--router:external` 的选项。若在创建 network 的时候指定了该选项，那么就可以从该 network 分配 floating ip。

## extension

*neutron/extensions/externl_net.py*

`class External_net(extensions.ExtensionDescriptor)`

## Model

*neutron/db/external_net_db.py*

`class ExternalNetwork(model_base.BASEV2)`

## `class External_net_db_mixin(object)`

WSGI 实现











