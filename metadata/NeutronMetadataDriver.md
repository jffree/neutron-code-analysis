# Neutron Metadata Driver

*neutron/agent/metatdata/driver.py*

* 查看正在运行的 `neutron-ns-metadata-proxy` 服务：

```
[root@CentOS-7 stack]# ps -aux | grep neutron-ns-meta
root     24422  0.0  0.0 112660   936 pts/23   S+   00:56   0:00 grep --color=auto neutron-ns-meta
stack    31151  0.0  0.3 235104 53096 ?        S    7月18   0:04 /usr/bin/python /usr/bin/neutron-ns-metadata-proxy --pid_file=/opt/stack/data/neutron/external/pids/4deddf7f-b13c-4bbc-b736-d9e871cd3af7.pid --metadata_proxy_socket=/opt/stack/data/neutron/metadata_proxy --router_id=4deddf7f-b13c-4bbc-b736-d9e871cd3af7 --state_path=/opt/stack/data/neutron --metadata_port=9697 --metadata_proxy_user=1001 --metadata_proxy_group=1001 --debug
```


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

* `metadata_port` metadata 服务的监听端口（在 l3_agent.ini 中：`metadata_port = 9697`）
* `metadata_access_mark` 在 l3_agent.ini 中：`metadata_access_mark = 0x1`

* 订阅资源事件
 1. 资源：`resources.ROUTER`；事件：`events.AFTER_CREATE`；回调方法：`after_router_added`
 2. 资源：`resources.ROUTER`；事件：`events.AFTER_UPDATE`；回调方法：`after_router_updated`
 3. 资源：`resources.ROUTER`；事件：`events.BEFORE_DELETE`；回调方法：`before_router_removed`



### `def spawn_monitored_metadata_proxy(cls, monitor, ns_name, port, conf, network_id=None, router_id=None)`

1. 用 `network_id` 或者 `router_id` 作为进程的标识
2. 调用 `_get_metadata_proxy_callback` 构造进程封装 `ProcessManager` 中的 `default_cmd_callback`（`ProcessManager` 会调用这个方法来创建具体要执行的命令）
3. 调用 `_get_metadata_proxy_process_manager` 创建一个 `ProcessManager` 实例 `pm`
4. 调用 `pm.enable` 启动命令
5. 调用 `monitor.register` 将上述创建的 pm 实例如在到监测中。

### `def _get_metadata_proxy_callback(cls, port, conf, network_id=None, router_id=None)`

用于构造执行 `neutron-ns-metadata-proxy` 的具体命令，例如：

```
/usr/bin/python /usr/bin/neutron-ns-metadata-proxy --pid_file=/opt/stack/data/neutron/external/pids/4deddf7f-b13c-4bbc-b736-d9e871cd3af7.pid --metadata_proxy_socket=/opt/stack/data/neutron/metadata_proxy --router_id=4deddf7f-b13c-4bbc-b736-d9e871cd3af7 --state_path=/opt/stack/data/neutron --metadata_port=9697 --metadata_proxy_user=1001 --metadata_proxy_group=1001 --debug
```

1. `network_id` 或者 `router_id` 必须要有一个
2. `metadata_proxy_socket` 指定 `neutron-ns-metadata-proxy` 的 `unix domain socket` 的位置。（在 *metadata_agent.ini* 定义：`metadata_proxy_socket = $state_path/metadata_proxy`）
3. 调用 `config.get_log_args` 进行日志选项的处理

### `def _get_metadata_proxy_process_manager(cls, router_id, conf, ns_name=None, callback=None)`

创建一个 `ProcessManager` 实例。

### `def _get_metadata_proxy_user_group_watchlog(cls, conf)`

获取运行该进程的有效用户、有效用户组、Log 是否可见

### `def destroy_monitored_metadata_proxy(cls, monitor, uuid, conf)`

1. 根据 uuid 取消在 monitor 中的检测
2. 调用 `_get_metadata_proxy_process_manager` 构造一个 `ProcessManager` 实例 pm
3. 调用 `pm.disable` 停止运行的命令






