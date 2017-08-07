# Neutron L3 Agent 之 PrefixDelegation

*neutron/agent/linux/pd.py*

## `class PrefixDelegation(object)`

```
    def __init__(self, context, pmon, intf_driver, notifier, pd_update_cb,
                 agent_conf):
        self.context = context
        self.pmon = pmon
        self.intf_driver = intf_driver
        self.notifier = notifier
        self.routers = {}
        self.pd_update_cb = pd_update_cb
        self.agent_conf = agent_conf
        self.pd_dhcp_driver = driver.DriverManager(
            namespace='neutron.agent.linux.pd_drivers',
            name=agent_conf.prefix_delegation_driver,
        ).driver
        registry.subscribe(add_router,
                           resources.ROUTER,
                           events.BEFORE_CREATE)
        registry.subscribe(remove_router,
                           resources.ROUTER,
                           events.AFTER_DELETE)
        self._get_sync_data()
```

1. 初始化一些属性
2. 加载 `prefix_delegation_driver` 驱动，默认为 `dibbler`（这里只是加载了，并没有实例化）
3. 通过回调系统注册感谢去资源
 1. resourece : ROUTER ; event : BEFORE_CREATE ; callback : add_router
 2. resourece : ROUTER ; event : AFTER_CREATE ; callback : remove_router
4. 调用 `_get_sync_data` 方法

```
neutron.agent.linux.pd_drivers =
    dibbler = neutron.agent.linux.dibbler:PDDibbler
```

### `def _get_sync_data(self)`

*我们暂时还未用到这里的功能，所以以后再进行分析*

1. 调用 `pd_dhcp_driver.get_sync_data` 方法

### `def after_start(self)`

l3 agent 启动后会调用

```
    def after_start(self):
        LOG.debug('SIGUSR1 signal handler set')
        signal.signal(signal.SIGUSR1, self._handle_sigusr1)
```

设定 `_handle_sigusr1` 来处理信号

### `def _handle_sigusr1(self, signum, frame)`

```
    def _handle_sigusr1(self, signum, frame):
        """Update PD on receiving SIGUSR1.

        The external DHCPv6 client uses SIGUSR1 to notify agent
        of prefix changes.
        """
        self.pd_update_cb()
```

这个 pd_update_cb 就是在初始化时由 `L3NATAgentWithStateReport` 传递过来的 `plugin_rpc.process_prefix_update` 方法。




















