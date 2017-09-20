from oslo_config import cfg
import oslo_messaging

ctxt = {'some': 'context'}
arg = 'This is a test'

transport = oslo_messaging.get_transport(cfg.CONF,'rabbit://stackrabbit:abc123@172.16.100.192:5672/')
#target = oslo_messaging.Target(topic='rpc_test', version='2.0')
target = oslo_messaging.Target(topic='rpc_test')
client = oslo_messaging.RPCClient(transport, target)
result = client.call(ctxt, 'test', arg=arg)
print result
