# Neutron ML2 之 RPC

## RPC 的初始化

### notifier 的初始化

* `Ml2Plugin` 在初始化时会调用 `_start_rpc_notifiers` 创建一个 RPC 的通知对象

```
    def _start_rpc_notifiers(self):
         """Initialize RPC notifiers for agents."""
         self.notifier = rpc.AgentNotifierApi(topics.AGENT)
         self.agent_notifiers[const.AGENT_TYPE_DHCP] = (
             dhcp_rpc_agent_api.DhcpAgentNotifyAPI()
         ) 
```

### listener 的初始化

* neutron-server 在引导完 WSGI 服务后会为各种的 worker 创建绿色线程：

*neutron/cmd/eventlet/server/__init__.py*

```
def main():
    server.boot_server(_main_neutron_server)
 
 
def _main_neutron_server():
    if cfg.CONF.web_framework == 'legacy':
        wsgi_eventlet.eventlet_wsgi_server()                                                                                                        
    else:
        wsgi_pecan.pecan_wsgi_server()
```

*neutron/server/wsgi_eventlet.py*

```
def eventlet_wsgi_server():
    neutron_api = service.serve_wsgi(service.NeutronApiService)
    start_api_and_rpc_workers(neutron_api)
 
 
def start_api_and_rpc_workers(neutron_api):
    try:                                                                                                                                            
        worker_launcher = service.start_all_workers()
...
```

*neutron/service.py*

```
def start_all_workers():
    workers = _get_rpc_workers() + _get_plugins_workers()                                                                                           
    return _start_workers(workers)

def _get_rpc_workers():
    plugin = manager.NeutronManager.get_plugin()                                                                                                                       
    service_plugins = (
        manager.NeutronManager.get_service_plugins().values())

    if cfg.CONF.rpc_workers < 1:
        cfg.CONF.set_override('rpc_workers', 1)

    # If 0 < rpc_workers then start_rpc_listeners would be called in a
    # subprocess and we cannot simply catch the NotImplementedError.  It is
    # simpler to check this up front by testing whether the plugin supports
    # multiple RPC workers.
    if not plugin.rpc_workers_supported():
        LOG.debug("Active plugin doesn't implement start_rpc_listeners")
        if 0 < cfg.CONF.rpc_workers:
            LOG.error(_LE("'rpc_workers = %d' ignored because "
                          "start_rpc_listeners is not implemented."),
                      cfg.CONF.rpc_workers)
        raise NotImplementedError()

    # passing service plugins only, because core plugin is among them
    rpc_workers = [RpcWorker(service_plugins,
                             worker_process_count=cfg.CONF.rpc_workers)]

    if (cfg.CONF.rpc_state_report_workers > 0 and
            plugin.rpc_state_report_workers_supported()):
        rpc_workers.append(
            RpcReportsWorker(
                [plugin],
                worker_process_count=cfg.CONF.rpc_state_report_workers
            )
        )
    return rpc_workers  
```

在 `class RpcWorker(neutron_worker.NeutronWorker)` 的 `start` 方法中会启动所有的 plugin 的 `start_rpc_listeners` 方法。

对于 core plugin 还会在 `RpcReportsWorker` 启动 `start_rpc_state_reports_listener` 方法。

* 那么在 `Ml2Plugin` 中 `start_rpc_listeners` 和 `start_rpc_state_reports_listener` 方法实现为：

```
    def _setup_rpc(self):
        """Initialize components to support agent communication."""
        self.endpoints = [                                                                                                                                             
            rpc.RpcCallbacks(self.notifier, self.type_manager),
            securitygroups_rpc.SecurityGroupServerRpcCallback(),
            dvr_rpc.DVRServerRpcCallback(),
            dhcp_rpc.DhcpRpcCallback(),
            agents_db.AgentExtRpcCallback(),
            metadata_rpc.MetadataRpcCallback(),
            resources_rpc.ResourcesPullRpcCallback()
        ]

    @log_helpers.log_method_call
    def start_rpc_listeners(self):
        """Start the RPC loop to let the plugin communicate with agents."""
        self._setup_rpc()
        self.topic = topics.PLUGIN
        self.conn = n_rpc.create_connection()
        self.conn.create_consumer(self.topic, self.endpoints, fanout=False)
        self.conn.create_consumer(
            topics.SERVER_RESOURCE_VERSIONS,
            [resources_rpc.ResourcesPushToServerRpcCallback()],
            fanout=True)
        # process state reports despite dedicated rpc workers
        self.conn.create_consumer(topics.REPORTS,
                                  [agents_db.AgentExtRpcCallback()],
                                  fanout=False)                                                                                                                        
        return self.conn.consume_in_threads()

    def start_rpc_state_reports_listener(self):
        self.conn_reports = n_rpc.create_connection()
        self.conn_reports.create_consumer(topics.REPORTS,
                                          [agents_db.AgentExtRpcCallback()],                                                                                           
                                          fanout=False)
        return self.conn_reports.consume_in_threads()
```