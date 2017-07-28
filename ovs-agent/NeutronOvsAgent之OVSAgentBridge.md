# Neutron Ovs Agent 之 OVSAgentBridge

*Common code for bridges used by OVS agent*

## `class OVSAgentBridge(ofswitch.OpenFlowSwitchMixin, br_cookie.OVSBridgeCookieMixin, ovs_lib.OVSBridge)`

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/ovs_bridge.py*

```
    _cached_dpid = None
```

### `def _get_dp(self)`

获取该 bridge 上 datapath 的信息（`dp, dp.ofproto, dp.ofproto_parser`）。

### `def setup_controllers(self, conf)`

为该 bridge 设定 controller

### `def drop_port(self, in_port)`

设定流表 从 `in_port` 进入的流量采取丢弃操作

## `class OpenFlowSwitchMixin(object)`

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/ofswitch.py*

**这个类完成了对 RYU 调用（流表的操作）的封装**

```
    def __init__(self, *args, **kwargs):
        self._app = kwargs.pop('ryu_app')
        super(OpenFlowSwitchMixin, self).__init__(*args, **kwargs)
```

### `def _get_dp_by_dpid(self, dpid_int)`

调用 `ofctl_api.get_datapath`

### `def _match(_ofp, ofpp, match, **match_kwargs)`

构造一个 `OFPMatch` 的对象

### `def _send_msg(self, msg, reply_cls=None, reply_multi=False)`

发送消息到交换机

调用 `ofctl_api.send_msg`

### ` def delete_flows(self, table_id=None, strict=False, priority=0, cookie=0, cookie_mask=0, match=None, **match_kwargs)`

删除流表

1. 调用 `_match` 构造 `OFPMatch` 对象
2. 构造 `OFPFlowMod` 消息对象
3. 调用 `_send_msg` 发送消息

### `def dump_flows(self, table_id=None)`

获取所有流表

1. 调用 `_get_dp` 获取 datapath
2. 构造 `OFPFlowStatsRequest` 的消息实例
3. 调用 `_send_msg` 发送消息，获取返回值

### `def install_instructions(self, instructions, table_id=0, priority=0, match=None, **match_kwargs)`

改变流表的动作。

### `def install_goto(self, dest_table_id, table_id=0, priority=0, match=None, **match_kwargs)`

调用 `install_instructions` 设置转发将符合该流表的流量转发到 `dest_table_id` 流表

### `def install_goto_next(self, table_id)`

将符合该流表的流量转发到下一个流表

### `def install_output(self, port, table_id=0, priority=0, match=None, **match_kwargs)`

设置符合条件（`match`） 的动作为 output

### `def install_normal(self, table_id=0, priority=0, match=None, **match_kwargs)`

设置符合条件（`match`） 的动作为 normal

### `def install_drop(self, table_id=0, priority=0, match=None, **match_kwargs)`

设置符合条件（`match`） 的动作为 drop

### `def install_apply_actions(self, actions, table_id=0, priority=0, match=None, **match_kwargs)`

设定对符合该流表的流量采取什么动作

## `class OVSBridgeCookieMixin(object)`

*Cookie：被 Remote Controller 用来筛选 Flow Statistics、Flow Modification 或者 Flow Deletion 行为的指示值*

* 这个类提供了对 ovs flow cookie 的处理。
 1. 将多有使用过的 cookie 放在 `_default_cookie` 变量中
 2. 新的 cookie 一定是未使用过的（也就是未放在 `_default_cookie` 变量中），请求成功后会也会放入 `_default_cookie` 中 

*neutron/plugins/ml2/drivers/openvswitch/agent/openflow/native/br_cookie.py*

```
class OVSBridgeCookieMixin(object):
    '''Mixin to provide cookie retention functionality
    to the OVSAgentBridge
    '''

    def __init__(self, *args, **kwargs):
        super(OVSBridgeCookieMixin, self).__init__(*args, **kwargs)
        self._reserved_cookies = set()
```

### `def reserved_cookies(self)`

属性方法，返回当前已经使用过的 cookie 值

### `def request_cookie(self)`

请求产生一个新的 cookie 值

### `def set_agent_uuid_stamp(self, val)`

手动设置一个 cookie 值

## `class OVSBridge(BaseOVS)`

*neutron/agent/common/ovs_lib.py*

请参考文章 *neutron/agent/NeutronAgent之OVS_LIB*