# Neutron Ml2 之 Vlantransparent

*关于 vlan transparent 的概念请看后面的参考文章*

## extensions

*neutron/extensions/vlantransparent.py*

`class Vlantransparent(extensions.ExtensionDescriptor)`

### `def disable_extension_by_config(aliases)`

如果 `cfg.CONF.vlan_transparent` 为 False 则移除对该 extension 的支持

### `def get_vlan_transparent(network)`

获取 network 数据中 `vlan_transparent` 的信息

## WSGI

*neutron/db/vlantransparent_db.py*

## `class Vlantransparent_db_mixin(object)`

```
    def _extend_network_dict_vlan_transparent(self, network_res, network_db):
        network_res[vlantransparent.VLANTRANSPARENT] = (
            network_db.vlan_transparent)
        return network_res

    db_base_plugin_v2.NeutronDbPluginV2.register_dict_extend_funcs(
        attributes.NETWORKS, ['_extend_network_dict_vlan_transparent'])
```

## 参考

[VTP](http://baike.baidu.com/link?url=UM1SHepAHW6SA0BkNXlQ8LflZMbrms9kCtiCs3QrQOIC73ilGd5Ze5gDzm8vDoMd71wdRcG4Vdp6naDC29AYd_)