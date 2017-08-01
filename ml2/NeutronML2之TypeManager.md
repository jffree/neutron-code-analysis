# Neutron ML2 之 TypeManager

* 继承于 `stevedore.named.NamedExtensionManager`，为 Neutron 的网络类型实现插件式管理。

* 模块

_neutron/plugins/ml2/managers.py_

* 配置文件：

_/etc/neutron/neutron.conf_  
_/etc/neutron/plugins/ml2/ml2\_conf.ini_

* neutron 包信息文件

_setup.cfg_

## `__init__` 方法

1. 调用 `super(TypeManager, self).__init__` 加载 neutron 的类型驱动（`cfg.CONF.ml2.type_drivers`）
2. 调用 `_register_types` 构造一个类型名称与类型实例映射的字典（`self.drivers`）
3. 调用 `_check_tenant_network_types` 检查当前加载的网络类型中是否支持租户的网络类型（`cfg.CONF.ml2.tenant_network_types`）
4. 调用 `_check_external_network_type` 检查是否支持外网默认的网络类型（`cfg.CONF.ml2.external_network_type`）

_关于具体的配置信息，请大家参考手册。_

在 setup.cfg 中可以看到所有的 type driver：

```
neutron.ml2.type_drivers =
    flat = neutron.plugins.ml2.drivers.type_flat:FlatTypeDriver
    local = neutron.plugins.ml2.drivers.type_local:LocalTypeDriver
    vlan = neutron.plugins.ml2.drivers.type_vlan:VlanTypeDriver
    geneve = neutron.plugins.ml2.drivers.type_geneve:GeneveTypeDriver
    gre = neutron.plugins.ml2.drivers.type_gre:GreTypeDriver
    vxlan = neutron.plugins.ml2.drivers.type_vxlan:VxlanTypeDriver
```

## `def _register_types(self)`

## `def _check_tenant_network_types(self, types)`

## `def _check_external_network_type(self, ext_network_type)`

## `def initialize(self)`

调用所有的 type driver 的 `initialize` 方法

## `def _get_attribute(self, attrs, key)`

```
    def _get_attribute(self, attrs, key):
        value = attrs.get(key)
        if value is constants.ATTR_NOT_SPECIFIED:
            value = None
        return value
```

## `def create_network_segments(self, context, network, tenant_id)`

1. 调用 `_process_provider_create` 检查创建 provider network 数据的正确性，并获取 segment 数据
2. 若 segment 数据不为空（创建的是 provider network）：
 1. 调用 `reserve_provider_segment` 为该 network 保留一个数据库记录
 2. 调用 `_add_network_segment` 增加一个 `NetworkSegment` 数据库记录
3. 若 `external_network_type` 存在且要创建的 network 数据中 `router:external` 为 true，则
 1. 调用 `_allocate_ext_net_segment` 为 tenant network 分配一个 segment
 2. 调用 `_add_network_segment` 创建 `NetworkSegment` 创建数据库记录
4. 对于其他的 tenanat network，则：
 1. 调用 `_allocate_tenant_net_segment` 为 tenant network 分配一个 segment
 2. 调用 `_add_network_segment` 创建 `NetworkSegment` 创建数据库记录

## `def _process_provider_create(self, network)`

1. 验证创建 provider network 时的参数是否合法。（若是有了 `segments` 属性，则所有的 --provider: 都需要放在它里面）
2. 若是有 --provider:* 的属性，但是没有 segments 属性，则调用 `_process_provider_segment` 验证 provider 属性是否正确，并返回 segment 数据
3. 若是只含有 `segments` 属性，则调用 `_process_provider_segment` 验证 provider 属性是否正确，获取 segment 数据。然后调用 `mpnet.check_duplicate_segments` 方法检查 `segments` 中是否有重复的数据
4. 最终都会返回 segments 相关的数据

[openstack network api create network](https://developer.openstack.org/api-ref/networking/v2/index.html?expanded=create-network-detail)

## `def _process_provider_segment(self, segment)`

从 segment 数据中获取与 provider network 有关的属性，调用 `validate_provider_segment` 验证这些数据是否合法，若合法则返回这些数据。

## `def validate_provider_segment(self, segment)`

根据 segment 中的 network type 调用 type driver 的 `validate_provider_segment` 来验证数据是否合法

## `def is_partial_segment(self, segment)`

根据 segment 中的 network type 调用 type driver 的 `is_partial_segment` 来确定 segment id 是如何分配

## `def reserve_provider_segment(self, session, segment)`

根据 segment 中的 network type 调用 type driver 的 `reserve_provider_segment` 来保留一个 segment

## `def _add_network_segment(self, context, network_id, segment, segment_index=0)`

```
    def _add_network_segment(self, context, network_id, segment,
                             segment_index=0):
        segments_db.add_network_segment(
            context, network_id, segment, segment_index)
```

创建一个 `NetworkSegment` 的数据库记录，并通过回调系统发送 `PRECOMMIT_CREATE` 的通知

## `def _allocate_ext_net_segment(self, session)`

1. 获取 `external_network_type` 网络类型
2. 调用 `_allocate_segment` 为 tenant network 分配一个 segment

## `def _allocate_segment(self, session, network_type)`

根据 network type 调用 type driver 的 `allocate_tenant_segment` 为租户分配一个 segment

## `def _allocate_tenant_net_segment(self, session)`

调用 `_allocate_segment` 分配 tenant network segment

## `def network_matches_filters(self, network, filters)`

判断 network 是否在 filter 范围内

1. 若 network 中有 --provider 相关属性，则调用 `_get_provider_segment` 获取 segment 数据
2. 若 network 中有 segments 属性，则调用 `_get_attribute` 获取 segment 数据
3. 若以上两者都没有直接返回 true
4. 若有 segment 数据，则调用 `_match_segment` 检查 segment 数据是否在 filter 内，若在则返回 true，若不在则返回 false

## `def _match_segment(self, segment, filters)`

检查 segment 数据是否在 filter 内，若在则返回 true，若不在则返回 false

## `def extend_network_dict_provider(self, context, network)`

```
    def extend_network_dict_provider(self, context, network):
        # this method is left for backward compat even though it would be
        # easy to change the callers in tree to use the bulk function
        return self.extend_networks_dict_provider(context, [network])
```

## `def extend_networks_dict_provider(self, context, networks)`

1. 调用 `segments_db.get_networks_segments` 查询 `NetworkSegment` 数据库中关于 network 的记录
2. 调用 `_extend_network_dict_provider` 增加所有 network 的 segment 属性

## `def _extend_network_dict_provider(self, network, segments)` 

增加 network 的 segment 属性

## `def release_network_segments(self, session, network_id)`

释放该 network 的所有 segments

1. 调用 `segments_db.get_network_segments` 的所有 segment 记录
2. 调用 `release_network_segment` 逐一释放 segment

## `def release_network_segment(self, session, segment)`

根据 segment 中的 network type 调用 type driver 的 `release_segment` 来释放 segment

## `def allocate_dynamic_segment(self, context, network_id, segment)`

1. 调用 `segments_db.get_dynamic_segment` 查询是否已经有相关的数据库记录，若有则直接返回。
2. 根据 segment 中的 network type 调用 type driver 的 `reserve_provider_segment` 来分配 segment
3. 调用 `segments_db.add_network_segment` 来增加数据库记录

## `def release_dynamic_segment(self, session, segment_id)`

1. 调用 `segments_db.get_dynamic_segment` 查询是否已经有相关的数据库记录，若没有则直接返回。
2. 根据 segment 中的 network type 调用 type driver 的 `release_segment` 来回收 segment
3. 调用 `segments_db.delete_network_segment` 来删除数据库记录