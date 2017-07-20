# OVS 之 reconnect

该模块定义了一个维护网络连接状态的有限状态机（FSM，finite-state machine）。这个有限状态机不维护连接本身，只维护连接的状态。

## `class Reconnect(object)`

* Reconnect 定义了五种连接状态，分别是：`Void`、`Listening`、`Backoff`、`ConnectInProgress`、`Active`、`Idle`、`Reconnect`。每个状态都有如下属性：
 1. `name`：该状态的名称
 2. `is_connected`：该状态中是否进行的了网络连接
 3. `deadline`：该状态的失效时间
 4. `run`：FSM 的下一步动作

* `Void` 状态是该 FSM 刚实例化的状态，这个状态只会在这时出现一次。
 * 刚实例化完的 FSM 需要调用 `enable` 方法，来转换到 `Backoff` 状态
* `Listening`：表示 FSM 处于监听状态，passive 为 True
* `ConnectInProgress`：表示 FSM 处于正在尝试连接的状态
* `Active`：表示 FSM 已经处于连接状态

### `def __init__(self, now)`

初始化很多的属性

1. `name`：该对象的名称
2. `state`：状态
3. `state_entered`：进入当前状态的时间
4. `max_tries`：最大的尝试次数
5. `info_level`：日志的记录水平
6. `n_attempted_connections`：尝试连接的次数
7. `n_successful_connections`：成功连接的次数
8. `total_connected_duration`：总共的链接成功的时间（每次连接成功都会累加）
9. `last_connected`：最近一次连接成功的时间
10. `last_activity`：最近一次进入 active 状态的时间
11. `last_disconnected`：最近一次断开连接的时间
12. `creation_time`：该 `Reconnect` 对象创建的时间
13. `backoff`：距离下一次连接或者监听的间隔时间
14. `min_backoff`：距离下一次连接或者监听的最小间隔时间
15. `max_backoff`：距离下一次连接或者监听的最大间隔时间
16. `probe_interval`
17. `passive`：`passive` 为 True 时，FSM 会进行监听等待连接的到来。`passive` 为 False 时，会主动连接远程的 server。
18. `seqno`

### `def set_name(self, name)`

设置该对象的名称

### `def enable(self, now)`

使能该 reconnect

### `def __may_retry(self)`

是否可以再次尝试

### `def _transition(self, now, state)`

**FSM 进行状态的转换**

### `def set_probe_interval(self, probe_interval)`


### `def run(self, now)`

**FSM 下一步要采取的动作**

### `def is_passive(self)`

是否是 passive 模式

### `def listening(self, now)`

将 FSM 转向 `Listening` 状态

### `def connecting(self, now)`

将 FSM 转向 `ConnectInProgress` 状态

### `def connected(self, now)`

将 FSM 转向 `Active` 状态

### `def activity(self, now)`

将 FSM 转向 `Active` 状态

### `def timeout(self, now)`

根据 FSM 当前状态的 deadline 判断是否超时

### `def is_connected(self)`

根据 FSM 当前的状态，判断网络是否已经连接

### `def get_last_connect_elapsed(self, now)`

计算上次连接到现在的间隔时间

### `def get_last_disconnect_elapsed(self, now)`

计算上次断开连接到现在的间隔时间

### `def get_stats(self, now)`

返回当前 FSM 的状态信息

### `def set_quiet(self, quiet)`

若是 quiet 为真，则 log 的记录级别将设为 debug

若是 quiet 为假，则 log 的记录级别将设为 info

### `def is_enabled(self)`

判断该 FSM 是否已经执行过 enable 方法。也就是当前状态不再为 `Void`

### `def disable(self, now)`

将 FSM 转换到 `Void` 状态

### `def force_reconnect(self, now)`

将 FSM 转换到 `Reconnect` 状态

### `def disconnected(self, now, error)`

若 FSM 扔允许转换，则将 FSM 转换到 `Backoff` 状态，否则转换到 `Void` 状态。

### `def listen_error(self, now, error)`

监听失败时被调用。当 FSM 状态处于 `Listening` 时，会调用 `disconnected` 方法将 FSM 转换到 `Backoff` 状态，否则转换到 `Void` 状态。

### `def connect_failed(self, now, error)`

连接失败时被调用。状态先转换到 `ConnectInProgress` 再转换到 `Backoff` 或者 `Void` 状态。