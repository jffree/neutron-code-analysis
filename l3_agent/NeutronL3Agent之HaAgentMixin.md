# Neutron L3 Agent 之 Ha AgentMixin

*neutron/agent/l3/ha.py*

* 框架：
 1. l3 ha AgentMixin 是启动一个 unix domain 的 wsgi 服务（`L3AgentKeepalivedStateChangeServer`）
 2. 该 wsgi 服务内运行着一个 app（`KeepalivedStateChangeHandler`）
 3. 该 wsgi app 接收的请求中包含 ha_router_id 和 ha_router_state
 4. `ha.AgentMixin.enqueue_state_change` 根据接收到的数据，进行相应的业务处理：
  1. 若支持 ipv6，则设定 master ha router 支持自动学习 ipv6 网关地址的功能
  2. 在 master ha router 上启动 metadata proxy 功能
  3. 在 master ha router 上启动 radvd 服务
  4. 发送 RPC 消息，通知 Router Service 有 ha router state 改变

## `class AgentMixin(object)`

```
    def __init__(self, host):
        self._init_ha_conf_path()
        super(AgentMixin, self).__init__(host)
        self.state_change_notifier = batch_notifier.BatchNotifier(
            self._calculate_batch_duration(), self.notify_server)
        eventlet.spawn(self._start_keepalived_notifications_server)
```

1. 调用 `_init_ha_conf_path` 确定 ha 数据目录的存在（*/opt/stack/data/neutron/ha_confs*）
2. 调用 `_calculate_batch_duration` 计算 ha router 由 salve 切换至 master 的时间间隔
3. 
3. 初始化一个 `BatchNotifier` 的实例，用于发送 ha router 状态更新的消息
4. 开辟一个协程，运行 `_start_keepalived_notifications_server` 方法

### `def _init_ha_conf_path(self)`

```
    def _init_ha_conf_path(self):
        ha_full_path = os.path.dirname("/%s/" % self.conf.ha_confs_path)
        common_utils.ensure_dir(ha_full_path)
```

确保 ha 数据目录的存在。（本实例为 `/opt/stack/data/neutron/ha_confs/`）

### `def _calculate_batch_duration(self)`

计算 ha salve 切换至 master 所需要的时间。（ha router salve 会接收 master 发送的消息，当 3 次接收不到 master 消息时，会尝试自己变更为 Master）

### `def notify_server(self, batched_events)`

```
    def notify_server(self, batched_events):
        translated_states = dict((router_id, TRANSLATION_MAP[state]) for
                                 router_id, state in batched_events)
        LOG.debug('Updating server with HA routers states %s',
                  translated_states)
        self.plugin_rpc.update_ha_routers_states(
            self.context, translated_states)
```

1. 获取 router 转换后的状态
2. 调用 `plugin_rpc.update_ha_routers_states` 发送 router 状态更新的 RPC 消息

### `def check_ha_state_for_router(self, router_id, current_state)`

1. 调用 `_get_router_info` 获取当前 router 记录的 info
2. 将 current_state 与 router info 中记录的 state 对比，若发现 router 的 state 发生了变化，则调用 `BatchNotifier.queue_event` 记录该事件

### `def _start_keepalived_notifications_server(self)`

1. 初始化一个 `L3AgentKeepalivedStateChangeServer` 实例
2. 调用 `L3AgentKeepalivedStateChangeServer.run` 方法，该方法会启动一个 unix domain 的 wsgi server。
3. 该 wsgi server 会接受关于 router_id 和 router_state 的信息。
4. 在接收到信息后，会进一步调用 `ha.AgentMixin.enqueue_state_change` 方法，处理该信息。

### `def enqueue_state_change(self, router_id, state)`

1. 调用 `_get_router_info` 获取该 router 的 info
2. 调用 `_configure_ipv6_ra_on_ext_gw_port_if_necessary` 在支持 ipv6 的情况下，允许 ipv6 通过 ra 自动学习网关地址
3. 若是配置中设定了 `enable_metadata_proxy`，则调用 `_update_metadata_proxy` 更新 metadata proxy 服务的状态
4. 调用 `_update_radvd_daemon` 来更新该 router 上 radvd 服务的状态
5. 发送 RPC 消息，告诉 Server 端有 ha router state 的更新产生

### `def _configure_ipv6_ra_on_ext_gw_port_if_necessary(self, ri, state)`

1. 若该 ha router 为 master，且此 router 含有 gateway port，则：
 1. 调用 router_info 的 `get_external_device_name` 获取 gateway port 的名称
 2. 若此路由是 distributed，则 gateway port 所在的  namespace 为 ha_namesapce
 3. 若此路由是非 distributed，则 gateway port 所在的  namespace 为 ns_name
 4. 调用 router_info 的 `_enable_ra_on_gw` 方法，允许 gateway 自动学习 ipv6 的网关地址

### `def _update_metadata_proxy(self, ri, router_id, state)`

1. 若当前路由的 ha 状态为 master，则调用 `MetadataDriver.spawn_monitored_metadata_proxy` 启动 metadata proxy 服务
2. 若当前路由的 ha 状态不是 master，则调用 `MetadataDriver.destroy_monitored_metadata_proxy` 销毁该 router 上的 metadata proxy 服务

### `def _update_radvd_daemon(self, ri, state)`

1. 若该 ha router 为 master 状态，则启动 `radvd` 服务
2. 若该 ha router 不是 master 状态，则停止 `radvd` 服务

## `class L3AgentKeepalivedStateChangeServer(object)`

```
    def __init__(self, agent, conf):
        self.agent = agent
        self.conf = conf

        agent_utils.ensure_directory_exists_without_file(
            self.get_keepalived_state_change_socket_path(self.conf))
```

1. 调用 `get_keepalived_state_change_socket_path` 获取 `keepalived-state-change` 文件的路径
2. 调用 `ensure_directory_exists_without_file` 确保该目录存在并没有任何的文件在其下面

### `def get_keepalived_state_change_socket_path(cls, conf)`

```
    @classmethod
    def get_keepalived_state_change_socket_path(cls, conf):
        return os.path.join(conf.state_path, 'keepalived-state-change')
```

确定 keepalived-state-change 文件的目录

### `def run(self)`

1. 创建一个 `UnixDomainWSGIServer` 实例，用作 WSGI Server
2. 调用 `UnixDomainWSGIServer.start` 启动该 WSGI Server
3. 调用 `UnixDomainWSGIServer.wait` 等待消息 


## `class KeepalivedStateChangeHandler(object)`

```
    def __init__(self, agent):
        self.agent = agent
```

这个竟然是 WSGI 应用。


```
     @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        router_id = req.headers['X-Neutron-Router-Id']
        state = req.headers['X-Neutron-State']
        self.enqueue(router_id, state)
```

### `def enqueue(self, router_id, state)`

```
    def enqueue(self, router_id, state):
        LOG.debug('Handling notification for router '
                  '%(router_id)s, state %(state)s', {'router_id': router_id,
                                                     'state': state})
        self.agent.enqueue_state_change(router_id, state)
```

调用 `ha.AgentMixin.enqueue_state_change` 方法


## `class UnixDomainWSGIServer(wsgi.Server)`

```
class UnixDomainWSGIServer(wsgi.Server):
    def __init__(self, name, num_threads=None):
        self._socket = None
        self._launcher = None
        self._server = None
        super(UnixDomainWSGIServer, self).__init__(name, disable_ssl=True,
                                                   num_threads=num_threads)

    def start(self, application, file_socket, workers, backlog, mode=None):
        self._socket = eventlet.listen(file_socket,
                                       family=socket.AF_UNIX,
                                       backlog=backlog)
        if mode is not None:
            os.chmod(file_socket, mode)

        self._launch(application, workers=workers)

    def _run(self, application, socket):
        """Start a WSGI service in a new green thread."""
        logger = logging.getLogger('eventlet.wsgi.server')
        eventlet.wsgi.server(socket,
                             application,
                             max_size=self.num_threads,
                             protocol=UnixDomainHttpProtocol,
                             log=logger)
```

启动 unix domain wsgi server