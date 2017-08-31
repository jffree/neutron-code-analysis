# Neuton l3 agent 之 `NamespaceManager`

*neutron/agent/l2/namespace_manager.py*

这个类是通过 `with ... as ... :` 来使用的。


## `class NamespaceManager(object)`

```
    ns_prefix_to_class_map = {
        namespaces.NS_PREFIX: namespaces.RouterNamespace,
        dvr_snat_ns.SNAT_NS_PREFIX: dvr_snat_ns.SnatNamespace,
        dvr_fip_ns.FIP_NS_PREFIX: dvr_fip_ns.FipNamespace,
    }

    def __init__(self, agent_conf, driver, metadata_driver=None):
        """Initialize the NamespaceManager.

        :param agent_conf: configuration from l3 agent
        :param driver: to perform operations on devices
        :param metadata_driver: used to cleanup stale metadata proxy processes
        """
        self.agent_conf = agent_conf
        self.driver = driver
        self._clean_stale = True
        self.metadata_driver = metadata_driver
        if metadata_driver:
            self.process_monitor = external_process.ProcessMonitor(
                config=agent_conf,
                resource_type='router')
```

若存在 metatdata proxy 服务，则初始化一个 `ProcessMonitor` 实例

`_clean_stale` 表示清理不用的 namespace

### `def __enter__(self)`

```
    def __enter__(self):
        self._all_namespaces = set()
        self._ids_to_keep = set()
        if self._clean_stale:
            self._all_namespaces = self.list_all()
        return self
```

1. 初始化一些变量
2. 调用 `list_all` 方法获取当前 host 上的 namespace 

### `def list_all(self)`

调用 `IPWrapper.get_namespaces` 获取当前 host 上的所有 namespace 

### `def __exit__(self, exc_type, value, traceback)`

1. 若发生异常，则返回 false
2. 若 `_clean_stale` 则不作任何处理，返回 True
3. 对于所有跟踪的 namespace：
 1. 调用 `get_prefix_and_id` 获取 namespace 的前缀和 id
 2. 对于根据 id 判断哪些 namespace 不需要存在，然后调用 `_cleanup` 进行清理

### `def get_prefix_and_id(self, ns_name)`

1. 调用 `namespaces.get_prefix_from_ns_name` 获取 namespace 的前缀（例如：snat-61eaacf9-d4e0-4202-bac9-321da0ceaa69，snat 即是前缀）
2. 调用 `namespaces.get_id_from_ns_name` 获取 namespace 的 id 后缀（例如：snat-61eaacf9-d4e0-4202-bac9-321da0ceaa69，61eaacf9-d4e0-4202-bac9-321da0ceaa69 既是前缀）
3. 返回 namespace 的前缀和 id

### `def _cleanup(self, ns_prefix, ns_id)`

1. 根据 namespace 前缀在 `ns_prefix_to_class_map` 找到对应的类
2. 实例化对应的类为 ns
3. 若启用了 metadata 服务，则调用 `metadata_driver.destroy_monitored_metadata_proxy` 停掉该 ns-id 对应的 metadata proxy 服务
4. 调用 `ns.delete` 删除该 namespace 

### `def is_managed(self, ns_name)`

判断一个 namespace 是否是归 neutron 管理的

### `def keep_router(self, router_id)`

```
    def keep_router(self, router_id):
        self._ids_to_keep.add(router_id)
```

追踪当前 host 上的 router

### `keep_ext_net(self, ext_net_id)`

```
    def keep_ext_net(self, ext_net_id):
        self._ids_to_keep.add(ext_net_id)
```

追踪当前 host 上的 network

### `def ensure_router_cleanup(self, router_id)`

确保当前 host 上 namespace id 与 router_id 一致的都 namespace 都被清除

### `def ensure_snat_cleanup(self, router_id)`

确保该 router 的 snat namespace 被清理干净