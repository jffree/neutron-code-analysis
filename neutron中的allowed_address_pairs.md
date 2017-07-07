# Neutron allowed_address_pairs

## 前言

Neutron中有个  MAC/IP 防篡改的功能，即 PortSecurity，虚拟机只能以Neutron分配的 MAC/IP跟外界通行。

在两台或多台虚拟机内部利用 keepalived 通过 VRRP 做 HA，通过 VIP 对外部提供服务；这样为突破 PortSecurity 限制，首先需要修改这一组 VM 的 Port 的allowed_address_pair 来允许该端口上VIP的访问。

## 原理：

* 增加 `allowed_address_pairs` 之前的 port 信息

```
neutron port-show 08ccf4de-f6e2-4d4d-bcdf-55532e93f32f
```

```
    +-----------------------+--------------------------------------------------------------------------------------+  
    | Field                 | Value                                                                                |  
    +-----------------------+--------------------------------------------------------------------------------------+  
    | admin_state_up        | True                                                                                 |  
    | allowed_address_pairs |                                                                                      |  
    | binding:capabilities  | {"port_filter": true}                                                                |  
    | binding:host_id       | ci91szcmp004.webex.com                                                               |  
    | binding:vif_type      | ovs                                                                                  |  
    | device_id             | 232e6621-69cc-4631-8996-732d32e9e5a4                                                 |  
    | device_owner          | compute:nova                                                                         |  
    | extra_dhcp_opts       |                                                                                      |  
    | fixed_ips             | {"subnet_id": "bf4e762a-b4b4-4f03-80ea-20dd30ba7159", "ip_address": "10.224.148.51"} |  
    | id                    | 08ccf4de-f6e2-4d4d-bcdf-55532e93f32f                                                 |  
    | mac_address           | fa:16:3e:38:38:90                                                                    |  
    | name                  |                                                                                      |  
    | network_id            | 218203a4-bc92-4c0e-a245-654e0e3ccefe                                                 |  
    | security_groups       | 6fbd7353-ccfa-4e16-864b-79b74409d39f                                                 |  
    | status                | ACTIVE                                                                               |  
    | tenant_id             | 097ee4a7afe0436d8c261dd0aa131fd5                                                     |  
    +-----------------------+--------------------------------------------------------------------------------------+  
```

* 增加 `allowed_address_pair` 之前的防火墙规则：

```
# iptables -nvL neutron-openvswi-s08ccf4de-f  
Chain neutron-openvswi-s08ccf4de-f (1 references)  
 pkts bytes target     prot opt in     out     source               destination           
53112 6436K RETURN     all  --  *      *       10.224.148.51        0.0.0.0/0           MAC FA:16:3E:38:38:90   
    0     0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0   
```

* 为改 port 增加 `allowed_address_pair`

```
neutron port-update 08ccf4de-f6e2-4d4d-bcdf-55532e93f32f  --allowed_address_pairs list=true type=dict ip_address=10.224.148.59
```

* 增加 `allowed_address_pair` 后的 port 属性

```
neutron port-show 08ccf4de-f6e2-4d4d-bcdf-55532e93f32f
```

```
    +-----------------------+--------------------------------------------------------------------------------------+  
    | Field                 | Value                                                                                |  
    +-----------------------+--------------------------------------------------------------------------------------+  
    | admin_state_up        | True                                                                                 |  
    | allowed_address_pairs | {"ip_address": "10.224.148.59", "mac_address": "fa:16:3e:38:38:90"}                  |  
    | binding:capabilities  | {"port_filter": true}                                                                |  
    | binding:host_id       | ci91szcmp004.webex.com                                                               |  
    | binding:vif_type      | ovs                                                                                  |  
    | device_id             | 232e6621-69cc-4631-8996-732d32e9e5a4                                                 |  
    | device_owner          | compute:nova                                                                         |  
    | extra_dhcp_opts       |                                                                                      |  
    | fixed_ips             | {"subnet_id": "bf4e762a-b4b4-4f03-80ea-20dd30ba7159", "ip_address": "10.224.148.51"} |  
    | id                    | 08ccf4de-f6e2-4d4d-bcdf-55532e93f32f                                                 |  
    | mac_address           | fa:16:3e:38:38:90                                                                    |  
    | name                  |                                                                                      |  
    | network_id            | 218203a4-bc92-4c0e-a245-654e0e3ccefe                                                 |  
    | security_groups       | 6fbd7353-ccfa-4e16-864b-79b74409d39f                                                 |  
    | status                | ACTIVE                                                                               |  
    | tenant_id             | 097ee4a7afe0436d8c261dd0aa131fd5                                                     |  
    +-----------------------+--------------------------------------------------------------------------------------+   
```

* 增加 `allowed_address_pair` 之后的防火墙规则：

```
    # iptables -nvL neutron-openvswi-s08ccf4de-f  
    Chain neutron-openvswi-s08ccf4de-f (1 references)  
     pkts bytes target     prot opt in     out     source               destination           
        3   252 RETURN     all  --  *      *       10.224.148.59        0.0.0.0/0           MAC FA:16:3E:38:38:90   
    53112 6436K RETURN     all  --  *      *       10.224.148.51        0.0.0.0/0           MAC FA:16:3E:38:38:90   
        0     0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0   
```

## extension

*neutron/extension/allowedaddresspairs.py*

`class Allowedaddresspairs(extensions.ExtensionDescriptor)`


## WSGI 实现

*neutron/db/allowedaddresspairs_db.py*

## `class AllowedAddressPairsMixin(object)`

```
    # Register dict extend functions for ports
    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attr.PORTS, ['_extend_port_dict_allowed_address_pairs'])
```

构造 port 的字典型数据时，会调用该方法，将该 port 的 `allowed_address_pairs` 属性增加进去

### `def _extend_port_dict_allowed_address_pairs(self, port_res, port_db)`	

* `port_res` ： port 数据库的字典格式
* `prot_db` ： port 数据库记录

调用 `_make_allowed_address_pairs_dict` 将与 `port_db` 相关联的 `AllowedAddressPair` 数据库的记录将其转换为字典格式，并加入到 `port_res` 里面

### `def _make_allowed_address_pairs_dict(self, allowed_address_pairs, fields=None)`

根据 `AllowedAddressPair` 数据库的记录将其转换为字典格式

```
    def _make_allowed_address_pairs_dict(self, allowed_address_pairs,
                                         fields=None):
        res = {'mac_address': allowed_address_pairs['mac_address'],
               'ip_address': allowed_address_pairs['ip_address']}
        return self._fields(res, fields)
```

## `def get_allowed_address_pairs(self, context, port_id)`

1. 调用 `_get_allowed_address_pairs_objs` 获取与该 port 绑定的 `AllowedAddressPair` 数据库记录
2. 调用 `_make_allowed_address_pairs_dict` 将数据库记录转化为易读格式

### `def _get_allowed_address_pairs_objs(self, context, port_id)`   

根据 port 的 ID 查询 `AllowedAddressPair` 的数据库记录并返回

```
    def _get_allowed_address_pairs_objs(self, context, port_id):
        pairs = obj_addr_pair.AllowedAddressPair.get_objects(
            context, port_id=port_id)
        return pairs
```

### `def update_address_pairs_on_port(self, context, port_id, port, original_port, updated_port)`

* `id`：port 的 id
* `prot`：待更新的数据
* `original_port`：未更新前的 port 的易读类型的数据
* `updated_port`：调用 `super(Ml2Plugin, self).update_port` 更新后的 port 的易读类型的数据（这里的更新应该是只更新了 port 的部分属性，因为有些属性是没有更新的）

1. 获取 port 待更新数据中的 `allowed_address_pairs` 的数据
2. 调用 `is_address_pairs_attribute_updated` 判断是否更新了 `allowed_address_pairs` 属性
3. 若是更新了 `allowed_address_pairs` 属性，则在 `updated_port` 数据中增加记录，同时调用 `_delete_allowed_address_pairs` 删除之前的 `allowed_address_pairs` 数据库记录，调用 `_process_create_allowed_address_pairs` 创建新的 `allowed_address_pairs` 数据库记录
4. 更新成功返回 True
5. 无更新返回 False

### `def is_address_pairs_attribute_updated(self, port, update_attrs)`

判断是否更新了 `allowed_address_pairs` 属性

### `def _delete_allowed_address_pairs(self, context, id)`

调用 `_get_allowed_address_pairs_objs` 获取数据库记录，然后删除这些记录

### `def _process_create_allowed_address_pairs(self, context, port, allowed_address_pairs)`

在 `allowed_address_pairs` 数据中不包含 `mac_address` 属性的话，则默认使用该 port 的 `mac_address`

创建 `allowed_address_pairs` 的数据库记录

### `def _has_address_pairs(self, port)`



### `def _check_update_has_allowed_address_pairs(self, port)`


### `def _check_update_deletes_allowed_address_pairs(self, port)`






## 数据库

*neutron/db/models/allowed_address_pair.py*

`class AllowedAddressPair(model_base.BASEV2)`


## 参考

[Neutron havana allow address pairs](http://blog.csdn.net/matt_mao/article/details/19417451)
[OpenStack VM单网卡多IP解决方法](https://xiexianbin.cn/openstack/2017/03/17/openstack-vm-single-network-card-multiple-ips)