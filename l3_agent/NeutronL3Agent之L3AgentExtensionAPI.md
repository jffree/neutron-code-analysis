# Neutron L3 Agent 之 `L3AgentExtensionAPI`

*neutron/agent/l3/l3_agent*

## `class L3AgentExtensionAPI(object)`

*封装了一些 extension 用到的 api*

```
    def __init__(self, router_info):
        self._router_info = router_info
```

### `def _local_namespaces(self)`

获取当前 host 上的 namespace 列表

相当于执行 `ip netns list` 命令

### `def get_router_hosting_port(self, port_id)`

根据 port id 获取该 port 的 router 信息

### `def is_router_in_namespace(self, router_id)`

根据 router_id 判断，判断该 router 是否在当前的 host 的 namespace 下

### `def get_routers_in_project(self, project_id)`

根据 project id 获取该 project 在当前 host 上的所有 router info


## `class L3AgentExtensionsManager(agent_ext_manager.AgentExtensionsManager)`

```
    def __init__(self, conf):
        super(L3AgentExtensionsManager, self).__init__(conf,
                L3_AGENT_EXT_MANAGER_NAMESPACE)
```

加载 l3 agent 的 extension，默认为空，未加载任何的 extension

```
   def add_router(self, context, data):
        """Notify all agent extensions to add router."""
        for extension in self:
            if hasattr(extension.obj, 'add_router'):
                extension.obj.add_router(context, data)
            else:
                LOG.error(
                    _LE("Agent Extension '%(name)s' does not "
                        "implement method add_router"),
                    {'name': extension.name}
                )

    def update_router(self, context, data):
        """Notify all agent extensions to update router."""
        for extension in self:
            if hasattr(extension.obj, 'update_router'):
                extension.obj.update_router(context, data)
            else:
                LOG.error(
                    _LE("Agent Extension '%(name)s' does not "
                        "implement method update_router"),
                    {'name': extension.name}
                )

    def delete_router(self, context, data):
        """Notify all agent extensions to delete router."""
        for extension in self:
            if hasattr(extension.obj, 'delete_router'):
                extension.obj.delete_router(context, data)
            else:
                LOG.error(
                    _LE("Agent Extension '%(name)s' does not "
                        "implement method delete_router"),
                    {'name': extension.name}
                )
```

逻辑很清晰，若 l3 agent 加载了相应的 extension，则每次对 router 进行增加、更新和删除操作时，都会调用这些 extension 的相应方法。

从 setup.cfg 来看，目前还没有实现的 l3 agent extension。