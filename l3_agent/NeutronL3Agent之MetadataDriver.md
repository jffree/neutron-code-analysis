# Neutron l3 agent 之 MetadataDriver

*neutron/agent/metadata/driver.py*

## `class MetadataDriver(object)`

```
    monitors = {}

    def __init__(self, l3_agent):
        self.metadata_port = l3_agent.conf.metadata_port
        self.metadata_access_mark = l3_agent.conf.metadata_access_mark
        registry.subscribe(
            after_router_added, resources.ROUTER, events.AFTER_CREATE)
        registry.subscribe(
            after_router_updated, resources.ROUTER, events.AFTER_UPDATE)
        registry.subscribe(
            before_router_removed, resources.ROUTER, events.BEFORE_DELETE)
```

* `metadata_port` 默认为 9697
* `metadata_access_mark` 默认为 0x1（*Iptables mangle mark used to mark metadata valid requests.*）
* 在系统回调中的感兴趣资源及其事件
 1. resource : `ROUTER` ;  event : `AFTER_CREATE` ; callback : `after_router_added`
 2. resource : `ROUTER` ;  event : `AFTER_UPDATE` ; callback : `after_router_updated`
 3. resource : `ROUTER` ;  event : `BEFORE_DELETE` ; callback : `before_router_removed`

### `def metadata_filter_rules(cls, port, mark)`

设定 metadata 的包过滤的 iptables 中 filter 表的规则

```
iptables -t filter -A INPUT -m mark --mark 0x1/0xffff -j ACCEPT
iptables -t filter -A INPUT -p tcp -m tcp --dport 9697 -j DROP
```

### `def metadata_mangle_rules(cls, mark)`

设定 metadata 的包过滤的 iptables 中 mangle 表的规则

```
iptables -t mangle -A PREROUTING -d 169.254.169.254/32 -i qr-+ -p tcp -m tcp --dport 80 -j MARK --set-xmark 0x1/0xffff
```

### `def metadata_nat_rules(cls, port)`

设定 metadata 的包过滤的 iptables 中 nat 表的规则

```
iptables -t nat -A PREROUTING -d 169.254.169.254/32 -i qr-+ -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 9697
```

### `def _get_metadata_proxy_user_group_watchlog(cls, conf)`

获取 metadata proxy 的 user、group 和 watchlog

### `def _get_metadata_proxy_callback(cls, port, conf, network_id=None, router_id=None)`

该方法用于在生成要执行的外部进程的命令。

1. network_id 或 router_id 必须有一个
2. 定义一个内部方法 `callback` 用来生成具体的命令

```
neutron-ns-metadata-proxy --pid_file=/opt/stack/data/neutron/external/pids/61eaacf9-d4e0-4202-bac9-321da0ceaa69.pid --metadata_proxy_socket=/opt/stack/data/neutron/metadata_proxy --router_id=61eaacf9-d4e0-4202-bac9-321da0ceaa69 --state_path=/opt/stack/data/neutron --metadata_port=9697 --metadata_proxy_user=1000 --metadata_proxy_group=1000 --debug
```

### `def _get_metadata_proxy_process_manager(cls, router_id, conf, ns_name=None, callback=None)`

创建一个 `ProcessManager` 实例，用来监测 metadata proxy 进程

### `def spawn_monitored_metadata_proxy(cls, monitor, ns_name, port, conf, network_id=None, router_id=None)`

启动 metatdata proxy 进程并监测其状态

1. 调用 `_get_metadata_proxy_callback` 获取构造执行命令的方法
2. 调用 `_get_metadata_proxy_process_manager` 获取监测执行命令的 `ProcessManager` 实例
3. 调用 `ProcessManager.enable` 启动该外部进程
4. 调用 `ProcessMonitor.register` 注册 `ProcessManager` 的实例，用来监测该进程的状态
5. 记录该 router 上的 `ProcessMonitor` 实例

### `def destroy_monitored_metadata_proxy(cls, monitor, uuid, conf)`

1. 调用 `ProcessMonitor.unregister` 取消对 metadata proxy 进程的检测
2. 调用 `_get_metadata_proxy_process_manager` 获取 metatdata proxy 的包装，`ProcessManager` 实例
3. 调用 `ProcessManager.disable` 停止该外部进程
4. 取消对该进程的记录

## `def after_router_added(resource, event, l3_agent, **kwargs)`

当在该 l3 agent 上创建了新的 router 后，会做如下操作：

1. 调用 `MetadataDriver.metadata_filter_rules` 获取 filter 表的 Metatdata 数据包的规则
2. 调用 `MetadataDriver.metadata_mangle_rules` 获取 mangle 表的 Metatdata 数据包的规则
3. 调用 `MetadataDriver.metadata_nat_rules` 获取 nat 表的 Metatdata 数据包的规则
4. 调用 `iptables_manager` 完成上述规则的添加
5. 若该 router 不是个 ha router，则调用 `MetadataDriver.spawn_monitored_metadata_proxy` 为该 router 启动提供 metadata 服务的进程

## `def after_router_updated(resource, event, l3_agent, **kwargs)`

根据 `MetadataDriver.monitors` 查看是否已经为该 router 创建了 metadata 服务，若没有，则调用 `after_router_added` 创建

## `def before_router_removed(resource, event, l3_agent, **kwargs)`

调用 `MetadataDriver.destroy_monitored_metadata_proxy` 销毁该 router 上的 metadata 服务