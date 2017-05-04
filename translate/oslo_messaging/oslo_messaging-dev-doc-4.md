# oslo_messaging developer doc

## Serializer

### `class oslo_messaging.Serializer`

Generic (de-)serialization definition base class.

### `deserialize_context(ctxt)`

Deserialize a dictionary into a request context.

**Parameters:**
	
* ctxt – Request context dictionary

**Returns:**	Deserialized form of entity

## `deserialize_entity(ctxt, entity)`

Deserialize something from primitive form.

**Parameters:**	

* ctxt – Request context, in deserialized form
* entity – Primitive to be deserialized

**Returns:** Deserialized form of entity

#### `serialize_context(ctxt)`

Serialize a request context into a dictionary.

**Parameters:**
	
* ctxt – Request context

**Returns:**	Serialized form of context

#### `serialize_entity(ctxt, entity)`

Serialize something to primitive form.

**Parameters:**
	
* ctxt – Request context, in deserialized form
* entity – Entity to be serialized

**Returns:** Serialized form of entity

### `class oslo_messaging.NoOpSerializer`

A serializer that does nothing.

## Exceptions

### `exception oslo_messaging.ClientSendError(target, ex)`

Raised if we failed to send a message to a target.

### `exception oslo_messaging.DriverLoadFailure(driver, ex)`

Raised if a transport driver can’t be loaded.

### `exception oslo_messaging.ExecutorLoadFailure(executor, ex)`

Raised if an executor can’t be loaded.

### `exception oslo_messaging.InvalidTransportURL(url, msg)`

Raised if transport URL is invalid.

### `exception oslo_messaging.MessagingException`

Base class for exceptions.

### `exception oslo_messaging.MessagingTimeout`
Raised if message sending times out.

### `exception oslo_messaging.MessagingServerError`
Base class for all MessageHandlingServer exceptions.

### `exception oslo_messaging.NoSuchMethod(method)`
Raised if there is no endpoint which exposes the requested method.

### `exception oslo_messaging.RPCDispatcherError`
A base class for all RPC dispatcher exceptions.

### `exception oslo_messaging.RPCVersionCapError(version, version_cap)`

### `exception oslo_messaging.ServerListenError(target, ex)`
Raised if we failed to listen on a target.

### `exception oslo_messaging.UnsupportedVersion(version, method=None)`
Raised if there is no endpoint which supports the requested version.

# other

## [Configuration Options](https://docs.openstack.org/developer/oslo.messaging/opts.html)

## [Testing Configurations](https://docs.openstack.org/developer/oslo.messaging/conffixture.html)

## [Available Drivers](https://docs.openstack.org/developer/oslo.messaging/drivers.html)

## [Supported Messaging Drivers](https://docs.openstack.org/developer/oslo.messaging/supported-messaging-drivers.html)

## [AMQP 1.0 Protocol Driver Deployment Guide](https://docs.openstack.org/developer/oslo.messaging/AMQP1.0.html)

## [Pika Driver Deployment Guide](https://docs.openstack.org/developer/oslo.messaging/pika_driver.html)

## [ZeroMQ Driver Deployment Guide](https://docs.openstack.org/developer/oslo.messaging/zmq_driver.html)

## [Guide for Transport Driver Implementors](https://docs.openstack.org/developer/oslo.messaging/driver-dev-guide.html)

## [Frequently Asked Questions](https://docs.openstack.org/developer/oslo.messaging/FAQ.html)

## [Contributing](https://docs.openstack.org/developer/oslo.messaging/contributing.html)