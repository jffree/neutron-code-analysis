# oslo\_message与rabbitmq

oslo\_messaging 默认会使用 rabbitmq 作为底层的 transport，所以首先确保你的 rabbitmq 服务已经启动：`systemctl start rabbitmq-server`

我们直接从代码说起：

## server 端：

```
#coding=utf-8                                                                                                                        

from oslo_config import cfg 
import oslo_messaging
import time

class ServerControlEndpoint(object):

    target =oslo_messaging.Target(namespace='control',
                                  version='2.0')

    def __init__(self, server):
        self.server = server

    def stop(self, ctx):
        print "------ServerControlEndpoint. stop --------"
        if self.server:
            self.server.stop()

class TestEndpoint(object):

    def test(self, ctx, arg):
        print "------ TestEndpoint.test -------"
        return arg

transport = oslo_messaging.get_transport(cfg.CONF)

#从cfg对象中，读取transport_url,rpc_backend和control_exchange信息构
#造Transport对象，其中rpc_backend和control_exchange的默认值分别为：’rabbit’和’openstack’。

target= oslo_messaging.Target(topic='test', server='server1')

#在构造RPC-server的target时，需要topic和server参数，exchange参数可选。

endpoints= [
    ServerControlEndpoint(None),
    TestEndpoint(),
]

#一个RPC-server可以暴露多个endpoint，每个endpoint包含一组方法，这组
#方法可以被RPC-client通过某种Transport对象远程调用。

server= oslo_messaging.get_rpc_server(transport, target, endpoints,
                                      executor='blocking')                                                                           

#构造RPC-server对象，其中executor有两种方式：blocking和eventlet。
#blocking：用户调用start函数后，在start函数中开始请求处理循环，用户线程
#阻塞，处理下一个请求。直到用户调用了stop函数后，这个处理循环才退出。
#消息的接受和分发处理都在调用start函数的线程中完成的。
#eventlet：在这种方式中，会有一个协程GreenThread来处理消息的接收，然后
#有其他不同GreenThread来处理不同消息的分发处理。调用start的用户线程不会被阻塞。
#在这里我们使用blocking方式。

try:
    server.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
   print("Stopping server")

server.stop()
server.wait()
```

* 启动 server： `python server.py`，然后我们用 `rabbitmqctl` 命令查看效果：

```
[root@wlw mkiso]# rabbitmqctl list_users
Listing users ...
guest   [administrator]

[root@wlw mkiso]# rabbitmqctl list_connections
Listing connections ...
guest   127.0.0.1       60282   running

[root@wlw mkiso]# rabbitmqctl list_channels                                                                                          
Listing channels ...
<rabbit@wlw.3.476.0>    guest   3       0

[root@wlw mkiso]# rabbitmqctl list_exchanges                                                                                         
Listing exchanges ...
openstack       topic
test_fanout     fanout
amq.rabbitmq.log        topic
amq.direct      direct
amq.match       headers
amq.topic       topic
amq.rabbitmq.trace      topic
        direct
amq.fanout      fanout
amq.headers     headers

[root@wlw mkiso]# rabbitmqctl list_queues                                                                                            
Listing queues ...
test.server1    0
test_fanout_499030ba736c4b538d4bb71e623c0bee    0
test    0

[root@wlw mkiso]# rabbitmqctl list_bindings                                                                                          
Listing bindings ...
        exchange        test    queue   test    []
        exchange        test.server1    queue   test.server1    []
        exchange        test_fanout_499030ba736c4b538d4bb71e623c0bee    queue   test_fanout_499030ba736c4b538d4bb71e623c0bee    []
openstack       exchange        test    queue   test    []
openstack       exchange        test.server1    queue   test.server1    []
test_fanout     exchange        test_fanout_499030ba736c4b538d4bb71e623c0bee    queue   test    []

[root@wlw mkiso]# rabbitmqctl list_consumers
Listing consumers ...
test.server1    <rabbit@wlw.3.476.0>    2       true    0       []
test_fanout_499030ba736c4b538d4bb71e623c0bee    <rabbit@wlw.3.476.0>    3       true    0       []
test    <rabbit@wlw.3.476.0>    1       true    0       []
```

* 可以看出：
  1. 启动 server 后，会创建一个到 rabbitmq-server 的 tcp 连接，以 guest 用户访问
  2. 在这个连接上会创建一个 channel
  3. 在这个 channel 上会创建两个 exchange：一个是 topic 类型的名为 openstack；另一个是 fanout 类型的名为 test\_fanout
  4. 同时创建了三个 queue
  5. 建立了 6 个 bind
  6. 创建一个 consumer

## client 端

```
#coding=utf-8                                                                                                                        

from oslo_config import cfg
import oslo_messaging as messaging

transport = messaging.get_transport(cfg.CONF)
target = messaging.Target(topic='test')

#在构造RPC-client的target时，需要topic参数，其他可选。

client = messaging.RPCClient(transport, target)
ret= client.call(ctxt = {},
                  method = 'test',
                  arg = 'myarg')

#远程调用时，需要提供一个字典对象来指明调用的上下文，调用方法的名字和传
#递给调用方法的参数(用字典表示)。

cctxt = client.prepare(namespace='control', version='2.0')

#prepare函数用于修改RPC-client对象的Target对象的属性。

cctxt.cast({},'stop')
```

* 重启 `rabbitmq-server`，启动 client： `python client.py`，然后我们用 `rabbitmqctl` 命令查看效果：

```
[root@wlw mkiso]# rabbitmqctl list_users                                                                                             
Listing users ...
guest   [administrator]

[root@wlw mkiso]# rabbitmqctl list_connections                                                                                       
Listing connections ...
guest   127.0.0.1       60322   running
guest   127.0.0.1       60324   running

[root@wlw mkiso]# rabbitmqctl list_channels                                                                                          
Listing channels ...
<rabbit@wlw.2.375.0>    guest   1       0
<rabbit@wlw.2.392.0>    guest   0       0

[root@wlw mkiso]# rabbitmqctl list_exchanges                                                                                         
Listing exchanges ...
openstack       topic
reply_5f5c53e43eb24f92b70bddebe8aa45a8  direct

amq.rabbitmq.log        topic
amq.direct      direct
amq.match       headers
amq.topic       topic
amq.rabbitmq.trace      topic
        direct
amq.fanout      fanout
amq.headers     headers

[root@wlw mkiso]# rabbitmqctl list_queues 
Listing queues ...
reply_5f5c53e43eb24f92b70bddebe8aa45a8  0

[root@wlw mkiso]# rabbitmqctl list_bindings                                                                                          
Listing bindings ...
        exchange        reply_5f5c53e43eb24f92b70bddebe8aa45a8  queue   reply_5f5c53e43eb24f92b70bddebe8aa45a8  []
reply_5f5c53e43eb24f92b70bddebe8aa45a8  exchange        reply_5f5c53e43eb24f92b70bddebe8aa45a8  queue   reply_5f5c53e43eb24f92b70bddebe8aa45a8       []

[root@wlw mkiso]# rabbitmqctl list_consumers                                                                                         
Listing consumers ...
```

* 可以看到：
  1. 两次调用创建了两个 connection
  2. 每个 connection 有一个 channel
  3. 创建了一个 direct 类型的 exchange（reply\_5f5c53e43eb24f92b70bddebe8aa45a8） 和一个 topic 类型的 exchange（openstack）
  4. 创建了一个 queue
  5. 创建了两个 bind
  6. 没有创建 consume

## 同时启动 server 和 client

```
[root@wlw mkiso]# rabbitmqctl list_users
Listing users ...
guest   [administrator]

[root@wlw mkiso]# rabbitmqctl list_connections
Listing connections ...
guest   127.0.0.1       60282   running
guest   127.0.0.1       60302   running

[root@wlw mkiso]# rabbitmqctl list_channels
Listing channels ...
<rabbit@wlw.3.476.0>    guest   3       0
<rabbit@wlw.3.600.0>    guest   0       0

[root@wlw mkiso]# rabbitmqctl list_exchanges
Listing exchanges ...
openstack       topic
test_fanout     fanout
reply_fc0d39795a174cbe8e295fd4bbad2f34  direct
amq.rabbitmq.log        topic
amq.direct      direct
amq.match       headers
amq.topic       topic
amq.rabbitmq.trace      topic
        direct
amq.fanout      fanout
amq.headers     headers

[root@wlw mkiso]# rabbitmqctl list_queues
Listing queues ...
test.server1    0
test_fanout_499030ba736c4b538d4bb71e623c0bee    0
test    0
reply_fc0d39795a174cbe8e295fd4bbad2f34  0

[root@wlw mkiso]# rabbitmqctl list_bindings
Listing bindings ...
        exchange        reply_fc0d39795a174cbe8e295fd4bbad2f34  queue   reply_fc0d39795a174cbe8e295fd4bbad2f34  []
        exchange        test    queue   test    []
        exchange        test.server1    queue   test.server1    []
        exchange        test_fanout_499030ba736c4b538d4bb71e623c0bee    queue   test_fanout_499030ba736c4b538d4bb71e623c0bee    []
openstack       exchange        test    queue   test    []
openstack       exchange        test.server1    queue   test.server1    []
reply_fc0d39795a174cbe8e295fd4bbad2f34  exchange        reply_fc0d39795a174cbe8e295fd4bbad2f34  queue   reply_fc0d39795a174cbe8e295fd4bbad2f34       []
test_fanout     exchange        test_fanout_499030ba736c4b538d4bb71e623c0bee    queue   test    []

[root@wlw mkiso]# rabbitmqctl list_consumers
Listing consumers ...
test.server1    <rabbit@wlw.3.476.0>    2       true    0       []
test_fanout_499030ba736c4b538d4bb71e623c0bee    <rabbit@wlw.3.476.0>    3       true    0       []
test    <rabbit@wlw.3.476.0>    1       true    0       []
```

## 总结

1. server 端会创建 consumer （命名为 topic.server）来接受消息，而 client 端则不会
2. server 端会创建两个 exchange，一个用于广播信息（fanout），另一个用于发送和接受指定信息（topic）
3. client 端创建两个 exchange，一个用来发送信息\(topic\)，另一个用来接受反馈（direct）。
4. server 端创建三个 queue 和6个 bind，一个用来接收广播消息（所有的接受者），一个用来接收组消息（多个接收者），一个用来接收指定消息（单个接收者）
5. client 端创建一个 queue 和两个 bind，用来接收指定消息



