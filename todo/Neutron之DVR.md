# Neutron 之 DVR

* DVR : Distributed Virtual Router（分布式虚拟路由）

* 在没有 DVR 之前，所有跨子网的通讯，以及子网到外网的通讯都需要经过网络节点来转发：

![无DVR](http://img.blog.csdn.net/20140910133330031?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbWF0dF9tYW8=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)

* DVR 既是在所有启动 Neutron L3 Agent 的节点上都部署 Neutron router。从而实现：
 1. 对于东西向的流量， 流量会直接在计算节点之间传递。
 2. 对于南北向的流量，如果有floating ip，流量就直接走计算节点。如果没有floating ip，则会走网络节点。

![DVR](http://img.blog.csdn.net/20140910133608865?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbWF0dF9tYW8=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)

## extension

*neutron/extensions/dvr.py*

`class Dvr(extensions.ExtensionDescriptor)`

`class DVRMacAddressPluginBase(object)`

## WSGI

*neutron/db/dvr_mac_db.py*

`class DVRDbMixin(ext_dvr.DVRMacAddressPluginBase)`

### `def __new__(cls, *args, **kwargs)`

```
    def __new__(cls, *args, **kwargs):
        registry.subscribe(_delete_mac_associated_with_agent,
                           resources.AGENT, events.BEFORE_DELETE)
        return super(DVRDbMixin, cls).__new__(cls)
```

事件订阅。

### `def plugin(self)`

属性方法，获取 core plugin 的实例

### `def get_dvr_mac_address_by_host(self, context, host)`

调用 `_get_dvr_mac_address_by_host` 根据 host 获取 `dvr_host_macs` 的数据库记录

若是没有相关记录则调用 `_create_dvr_mac_address` 创建 `dvr_host_macs` 的数据库记录

### `def _create_dvr_mac_address(self, context, host)`

读取配置文件中的 `dvr_base_mac`

调用 `_create_dvr_mac_address_retry` 实现 mac 地址的创建，实现 `dvr_host_macs` 的数据库记录的创建

### `def _create_dvr_mac_address_retry(self, context, host, base_mac)`

1. 调用 `get_random_mac` 产生 Mac 地址
2. 创建 `dvr_host_macs` 的数据库记录
3. 调用 `get_dvr_mac_address_list` 获取所有 `dvr_host_macs` 的数据库记录
4. 调用 core plugin 实例的 `plugin.notifier.dvr_mac_address_update` 发送 rpc 消息
5. 调用 `_make_dvr_mac_address_dict` 返回创建后的信息

### `def get_dvr_mac_address_list(self, context)`

获取所有的 `dvr_host_macs` 的数据库记录

### `def _make_dvr_mac_address_dict(self, dvr_mac_entry, fields=None)`

```
    def _make_dvr_mac_address_dict(self, dvr_mac_entry, fields=None):
        return {'host': dvr_mac_entry['host'],
                'mac_address': dvr_mac_entry['mac_address']}
```


### `def _delete_mac_associated_with_agent(resource, event, trigger, context, agent, **kwargs)`

当有 agent 资源将被删除时，会调用该方法。

1. 获取 core plugin 的实例
2. 若是该 agent 所在的 host 还有别的 agent 则不作操作，直接返回
3. 若是该 agent 所在的 host 没有别的 agent 了，则删除该 host 的 `DistributedVirtualRouterMacAddress` （`dvr_host_macs`）数据库记录
4. 调用 core plugin 实例的 `get_dvr_mac_address_list` 方法获取所有的 `dvr_host_macs` 数据库记录
5. 调用 core plugin 实例的 `plugin.notifier.dvr_mac_address_update` 发送 rpc 消息

### `def get_subnet_for_dvr(self, context, subnet, fixed_ips=None)`

根据 `subnet` 和 `fixed_ips` 获取子网的详细信息（带有 `gateway_mac`，这个方法会通过 rpc 被调用）

### `def get_ports_on_host_by_subnet(self, context, host, subnet)`

获取提供 DVR 服务的 port

* `host`：host id 
* `subnet`：subnet id
* 
# 参考

[Scenario: High Availability using Distributed Virtual Routing (DVR)](https://docs.openstack.org/liberty/networking-guide/scenario-dvr-ovs.html)

[初探Openstack Neutron DVR ](http://blog.csdn.net/matt_mao/article/details/39180135)

[OpenStack Neutron 中的 DVR 简介与 OVS 流表分析](https://www.ibm.com/developerworks/cn/cloud/library/1509_xuwei_dvr/)