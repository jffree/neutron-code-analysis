# Neutron Service Plugin 之 Router Service

* 在 */etc/neutron/neutron.conf* 中我们可以看到这个配置选项：

```
service_plugins = neutron.services.l3_router.l3_router_plugin.L3RouterPlugin
```

正说明 neutron-server 加载了 router 这个 service plugin


## `class L3RouterPlugin`

```
class L3RouterPlugin(service_base.ServicePluginBase,
                     common_db_mixin.CommonDbMixin,
                     extraroute_db.ExtraRoute_db_mixin,
                     l3_hamode_db.L3_HA_NAT_db_mixin,
                     l3_gwmode_db.L3_NAT_db_mixin,
                     l3_dvr_ha_scheduler_db.L3_DVR_HA_scheduler_db_mixin,
                     dns_db.DNSDbMixin)
```

```
    supported_extension_aliases = ["dvr", "router", "ext-gw-mode",
                                   "extraroute", "l3_agent_scheduler",
                                   "l3-ha", "router_availability_zone",
                                   "l3-flavors"]

    __native_pagination_support = True
    __native_sorting_support = True

    @resource_registry.tracked_resources(router=l3_db.Router,
                                         floatingip=l3_db.FloatingIP)
    def __init__(self):
        self.router_scheduler = importutils.import_object(
            cfg.CONF.router_scheduler_driver)
        self.add_periodic_l3_agent_status_check()
        super(L3RouterPlugin, self).__init__()
        if 'dvr' in self.supported_extension_aliases:
            l3_dvrscheduler_db.subscribe()
        if 'l3-ha' in self.supported_extension_aliases:
            l3_hascheduler_db.subscribe()
        self.agent_notifiers.update(
            {n_const.AGENT_TYPE_L3: l3_rpc_agent_api.L3AgentNotifyAPI()})

        rpc_worker = service.RpcWorker([self], worker_process_count=0)

        self.add_worker(rpc_worker)
        self.l3_driver_controller = driver_controller.DriverController(self)
```

1. `router_scheduler_driver` : 默认为：`neutron.scheduler.l3_agent_scheduler.LeastRoutersScheduler`
2. 调用 `add_periodic_l3_agent_status_check` （在 `L3AgentSchedulerDbMixin` 中定义）
3. 调用父类的 `__init__` 方法
4. 若 router 支持 `dvr`，则调用系统的回调方法（`l3_dvrscheduler_db.subscribe`）来订阅如下资源事件：
 1. resource : `PORT`；event : `AFTER_UPDATE`；callback : `_notify_l3_agent_port_update`
 2. resource : `PORT`；event : `AFTER_CREATE`；callback : `_notify_l3_agent_new_port`
 3. resource : `PORT`；event : `AFTER_DELETE`；callback : `_notify_port_delete`
5. 若 router 支持 `l3-ha`，则调用系统的回调方法（`l3_hascheduler_db.subscribe`）来订阅如下资源事件：
 1. resource : `PORT`；event : `AFTER_UPDATE`；callback : `_notify_l3_agent_ha_port_update`
6. 增加一个 `agent_notifiers`：`L3AgentNotifyAPI`
7. 创建一个 `RpcWorker` 实例，并调用 `add_worker` 将其加入到工作队列中
8. 创建 `DriverController` 的实例

### `def get_plugin_type(cls)`

返回 router service plugin 的类型 `L3_ROUTER_NAT`

### `def get_plugin_description(self)`

返回 router service plugin 的描述

### `def start_rpc_listeners(self)`

创建一个 RPC Server 

### `def router_supports_scheduling(self, context, router_id)`

判断一个 router 是否支持调度

### `def create_floatingip(self, context, floatingip)`

调用 `L3_NAT_db_mixin.create_floatingip` 实现







