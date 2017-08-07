# Neutron L3 Agent 之 `L3AgentKeepalivedStateChangeServer`

*neutron/agent/l3/ha.py*


## `class L3AgentKeepalivedStateChangeServer(object)`

```
    def __init__(self, agent, conf):
        self.agent = agent
        self.conf = conf

        agent_utils.ensure_directory_exists_without_file(
            self.get_keepalived_state_change_socket_path(self.conf))
```

1. 调用 `ensure_directory_exists_without_file` 确保 ha 数据文件 必须存在

### `def get_keepalived_state_change_socket_path(cls, conf)`

```
    @classmethod
    def get_keepalived_state_change_socket_path(cls, conf):
        return os.path.join(conf.state_path, 'keepalived-state-change')
```

ha 数据文件的地址。（本例中为：*/opt/stack/data/neutron/keepalived-state-change*）

### `def run(self)`

```
    def run(self):
        server = agent_utils.UnixDomainWSGIServer(
            'neutron-keepalived-state-change',
            num_threads=self.conf.ha_keepalived_state_change_server_threads)
        server.start(KeepalivedStateChangeHandler(self.agent),
                     self.get_keepalived_state_change_socket_path(self.conf),
                     workers=0,
                     backlog=KEEPALIVED_STATE_CHANGE_SERVER_BACKLOG)
        server.wait()
```

`ha_keepalived_state_change_server_threads` 默认为 3

## `class KeepalivedStateChangeHandler(object)`

```
class KeepalivedStateChangeHandler(object):
    def __init__(self, agent):
        self.agent = agent

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        router_id = req.headers['X-Neutron-Router-Id']
        state = req.headers['X-Neutron-State']
        self.enqueue(router_id, state)

    def enqueue(self, router_id, state):
        LOG.debug('Handling notification for router '
                  '%(router_id)s, state %(state)s', {'router_id': router_id,
                                                     'state': state})
        self.agent.enqueue_state_change(router_id, state)
```













