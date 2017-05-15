# Notifier

## `class oslo_messaging.Notifier(transport, publisher_id=None, driver=None, serializer=None, retry=None, topics=None)`

Send notification messages.

通知器类通过消息传送或其他方式发送通知消息。

通知消息遵循以下格式：

```
{'message_id': six.text_type(uuid.uuid4()),
 'publisher_id': 'compute.host1',
 'timestamp': timeutils.utcnow(),
 'priority': 'WARN',
 'event_type': 'compute.create_instance',
 'payload': {'instance_id': 12, ... }}
```

通配符对象可以使用传输对象和发布者ID进行实例化：

```
notifier = messaging.Notifier(get_notification_transport(CONF),
‘compute’)
```

并通过驱动程序配置选项和通过[oslo_messaging_notifications]部分中的主题配置选项选择的主题发送通知。

或者，Notifier 对象可以使用特定的驱动程序或主题进行实例化：

```
transport = notifier.get_notification_transport(CONF)
notifier = notifier.Notifier(transport,
                             'compute.host',
                             driver='messaging',
                             topics=['notifications'])
```

通知程序对象实例化（主要是加载通知驱动程序的成本）相对较贵，因此可以使用`prepare()` 方法，使用不同的发布者id专门化给定的通告程序对象：

*实际上 prepare 方法是在现有的 Notifier 实例的基础上，创建一个一个它的子类实例。*

```
notifier = notifier.prepare(publisher_id='compute')
notifier.info(ctxt, event_type, payload)
```

### `audit(ctxt, event_type, payload)`

Send a notification at audit level.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `critical(ctxt, event_type, payload)`

Send a notification at critical level.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `debug(ctxt, event_type, payload)`

Send a notification at debug level.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `error(ctxt, event_type, payload)`

Send a notification at error level.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `info(ctxt, event_type, payload)`

Send a notification at info level.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `is_enabled()`

Check if the notifier will emit notifications anywhere.

* Returns:	
 1. false if the driver of the notifier is set only to noop, true otherwise

### `prepare(publisher_id=<object object>, retry=<object object>)`

Return a specialized Notifier instance.

* Returns a new Notifier instance with the supplied publisher_id. Allows sending notifications from multiple publisher_ids without the overhead of notification driver loading.

* Parameters:	

 1. `publisher_id (str)` – field in notifications sent, for example ‘compute.host1’
 2. retry (int) – connection retries configuration (used by the messaging driver): None or -1 means to retry forever. 0 means no retry is attempted. N means attempt at most N retries.

### `sample(ctxt, event_type, payload)`

Send a notification at sample level.

Sample notifications are for high-frequency events that typically contain small payloads. eg: “CPU = 70%”

Not all drivers support the sample level (log, for example) so these could be dropped.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `warn(ctxt, event_type, payload)`

Send a notification at warning level.

* Parameters:	
 1. ctxt (dict) – a request context dict 
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

### `warning(ctxt, event_type, payload)`

Send a notification at warning level.

* Parameters:	
 1. ctxt (dict) – a request context dict
 2. event_type (str) – describes the event, for example ‘compute.create_instance’
 3. payload (dict) – the notification payload

* Raises:	
 1. MessageDeliveryFailure

## `class oslo_messaging.LoggingNotificationHandler(url, publisher_id=None, driver=None, topic=None, serializer=None)`

Handler for logging to the messaging notification system.

每次应用程序使用日志记录模块记录消息时，它将作为通知发送。用于通知的严重性将与日志记录使用的严重性相同。

这可以通过以下方式用于Python日志记录配置：

```
[handler_notifier]
class=oslo_messaging.LoggingNotificationHandler
level=ERROR
args=('rabbit:///')
```

### `CONF = <oslo_config.cfg.ConfigOpts object>`

Default configuration object used, subclass this class if you want to use another one.

### `emit(record)`

Emit the log record to the messaging notification system.

* Parameters:	
 1. record – A log record to emit.

## `class oslo_messaging.LoggingErrorNotificationHandler(*args, **kwargs)`

# Available Notifier Drivers

## log

Publish notifications via Python logging infrastructure.

## messaging

Send notifications using the 1.0 message format.

This driver sends notifications over the configured messaging transport, but without any message envelope (also known as message format 1.0).

This driver should only be used in cases where there are existing consumers deployed which do not support the 2.0 message format.

## messagingv2

Send notifications using the 2.0 message format.

## noop

**Warning:** No documentation found in noop = oslo_messaging.notify._impl_noop:NoOpDriver

## routing

**Warning:** No documentation found in routing = oslo_messaging.notify._impl_routing:RoutingDriver

## test

Store notifications in memory for test verification.