# Neutron Ovs Agent 之 OVSAgentExtensionAPI

*neutron/plugins/ml2/drivers/openvswitch/agent/ovs_agent_extension_api.py*

## `class OVSAgentExtensionAPI(object)`

*Implements the Agent API for Open vSwitch agent.*

```
    def __init__(self, int_br, tun_br):
        super(OVSAgentExtensionAPI, self).__init__()
        self.br_int = int_br
        self.br_tun = tun_br
```

```
    def request_int_br(self):
        """Allows extensions to request an integration bridge to use for
        extension specific flows.
        """
        return OVSCookieBridge(self.br_int)

    def request_tun_br(self):
        """Allows extensions to request a tunnel bridge to use for
        extension specific flows.

        If tunneling is not enabled, this method will return None.
        """
        if not self.br_tun:
            return None

        return OVSCookieBridge(self.br_tun)
```

## `class OVSCookieBridge(object)`

对 ovs bridge flow 操作的封装，允许 extension 对 ovs flow entity 进行 add、mod、delete 操作

```
    def __init__(self, bridge):
        """:param bridge: underlying bridge
        :type bridge: OVSBridge
        """
        self.bridge = bridge
        self._cookie = self.bridge.request_cookie()
```

* 调用 `request_cookie`（`OVSBridgeCookieMixin` 中实现） 产生一个随机的 cookie

### `def default_cookie(self)`

```
    @property
    def default_cookie(self):
        return self._cookie
```

### `def do_action_flows(self, action, kwargs_list)`

```
    def do_action_flows(self, action, kwargs_list):
        # NOTE(tmorin): the OVSBridge code is excluding the 'del'
        # action from this step where a cookie
        # is added, but I think we need to keep it so that
        # an extension does not delete flows of another
        # extension
        for kw in kwargs_list:
            kw.setdefault('cookie', self._cookie)

            if action is 'mod' or action is 'del':
                kw['cookie'] = ovs_lib.check_cookie_mask(str(kw['cookie']))

        self.bridge.do_action_flows(action, kwargs_list)
```

### 其他方法

```
    def add_flow(self, **kwargs):
        self.do_action_flows('add', [kwargs])

    def mod_flow(self, **kwargs):
        self.do_action_flows('mod', [kwargs])

    def delete_flows(self, **kwargs):
        self.do_action_flows('del', [kwargs])

    def __getattr__(self, name):
        # for all other methods this class is a passthrough
        return getattr(self.bridge, name)

    def deferred(self, **kwargs):
        # NOTE(tmorin): we can't passthrough for deferred() or else the
        # resulting DeferredOVSBridge apply_flows method would call
        # the (non-cookie-filtered) do_action_flow of the underlying bridge
        return ovs_lib.DeferredOVSBridge(self, **kwargs)
```


