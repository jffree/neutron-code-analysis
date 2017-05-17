# oslo_messaging 中的 Notifier 在 neutron 中的使用。

## 初始化

*neutron/common/rpc.py*

```
def init(conf):
    global TRANSPORT, NOTIFICATION_TRANSPORT, NOTIFIER
    exmods = get_allowed_exmods()
    TRANSPORT = oslo_messaging.get_transport(conf,
                                             allowed_remote_exmods=exmods,
                                             aliases=TRANSPORT_ALIASES)
    NOTIFICATION_TRANSPORT = oslo_messaging.get_notification_transport(
        conf, allowed_remote_exmods=exmods, aliases=TRANSPORT_ALIASES)
    serializer = RequestContextSerializer()
    NOTIFIER = oslo_messaging.Notifier(NOTIFICATION_TRANSPORT,
                                       serializer=serializer)
```

### 构造 Notifier 的 transport `NOTIFICATION_TRANSPORT`

* **注意：**给 `oslo_messaging.get_notification_transport` 传递的参数中 `url` 为 None，则 Notifier 会采用同 rpc（oslo_messaging.message）相同的一样的 url。

### 构造 Notifier 的实例：`Notifier`
  
我们先看一下 */etc/neutron/neutron.conf* 中关于 oslo_messaging.Notifier 的配置：

```
[oslo_messaging_notifications]
#driver =
#transport_url = <None>
#topics = notifications
```

这三个选项分别对应着 Notifier 的：

1. 驱动（log、messaging....）
2. url（应该采用哪种 transport）
3. topic（传递消息时用到的 topic）

*在 devstack 默认的情况下是没有设置 driver 的，也就是虽然实例化了 Notifier，但是却无法发送消息。*

## 使用

我们举例说在 *neutron/api/v2/base.py* 中 `Contoller` 中使用的 Notifer：

### 在 `Controller.__init__` 中：

```
self._notifier = n_rpc.get_notifier('network')
``` 

### 在 *neutron/common/rpc.py* 中的 `get_notifier`

```
def get_notifier(service=None, host=None, publisher_id=None):
    assert NOTIFIER is not None
    if not publisher_id:
        publisher_id = "%s.%s" % (service, host or cfg.CONF.host)
    return NOTIFIER.prepare(publisher_id=publisher_id)
```

也就是在初始化 Notifier 的基础上更新了 `publisher_id`，相当于创建一个新的 `Notifier`实例（这样子可以避免驱动的加载）。

### 在 `Controller.create` 中：

```
        self._notifier.info(request.context,
                            self._resource + '.create.start',
                            body)
```

这里就会发送 Notifier 的消息。

# 参考

[Notifier](https://docs.openstack.org/developer/oslo.messaging/notifier.html) *我翻译过*

[Notification Driver](https://docs.openstack.org/developer/oslo.messaging/notification_driver.html)

[Notification Listener](https://docs.openstack.org/developer/oslo.messaging/notification_listener.html)

[oslo.messaging组件的学习之notify方法](http://bingotree.cn/?p=238)