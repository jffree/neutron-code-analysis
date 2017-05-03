# [OSProfiler](http://docs.openstack.org/developer/osprofiler)

OSProfiler是一个OpenStack跨项目分析库。

## Background

OpenStack 由多个项目组成。 而每个项目又由多个服务组成。在处理一些请求时，例如引导虚拟机，OpenStack 会使用来自不同项目的多个服务。在这种情况下，某些工作效率太低，这对于理解错误以及确定瓶颈来说是非常复杂的。

为了解决这个问题，我们介绍一个很小但功能强大的库 **osprofiler**，它将被所有OpenStack项目及其python客户端使用。 为了能够每个请求生成1个跟踪，它遍历及这个请求所涉及的所有服务，并构建一个调用树（参见[示例](http://pavlovic.me/rally/profiler/)）。

### Why not cProfile and etc?

这个库的范围是完全不同的：

* 我们的兴趣是从不同的服务中获取一个追踪点，而不是在一个进程内追踪所有的python调用。

* 这个库应该在OpenStack中易于集成。这意味着：

 * 整合项目的代码基础不应该太多变化。

 * 我们应该能够完全关掉它。

 * 我们应该能够在生产中以懒惰模式保持打开状态（例如，管理员应该可以追踪一个请求）。

## OSprofiler API

在使用API​​之前，您应该了解有关API的几件事情。

### 增加一个追踪点的5种方法

```
from osprofiler import profiler

def some_func():
    profiler.start("point_name", {"any_key": "with_any_value"})
    # your code
    profiler.stop({"any_info_about_point": "in_this_dict"})


@profiler.trace("point_name",
                info={"any_info_about_point": "in_this_dict"},
                hide_args=False)
def some_func2(*args, **kwargs):
    # If you need to hide args in profile info, put hide_args=True
    pass

def some_func3():
    with profiler.Trace("point_name",
                        info={"any_key": "with_any_value"}):
        # some code here

@profiler.trace_cls("point_name", info={}, hide_args=False,
                    trace_private=False)
class TracedClass(object):

    def traced_method(self):
        pass

    def _traced_only_if_trace_private_true(self):
         pass

@six.add_metaclass(profiler.TracedMeta)
class RpcManagerClass(object):
    __trace_args__ = {'name': 'rpc',
                      'info': None,
                      'hide_args': False,
                      'trace_private': False}

     def my_method(self, some_args):
         pass

     def my_method2(self, some_arg1, some_arg2, kw=None, kw2=None)
         pass
```

### How profiler works?

* `@profiler.Trace()` 和 `profiler.trace()` 只是语法糖，实际上是调用 `profiler.start()` 和 `profiler.stop()` 方法。

* `profiler.start()` ＆ `profiler.stop()` 的每次调用都会向收集器发送一条消息。这意味着每个跟踪点在收集器中创建两条记录。 （稍后会将更多的关于 collector & records 的信息）

* 支持嵌套跟踪点。以下示例产生2个跟踪点：

```
profiler.start("parent_point")
profiler.start("child_point")
profiler.stop()
profiler.stop()
```

实现相当简单。Profiler 具有一个包含所有跟踪点的ID的堆栈。例如：

```
profiler.start("parent_point") # trace_stack.push(<new_uuid>)
                               # send to collector -> trace_stack[-2:]

profiler.start("parent_point") # trace_stack.push(<new_uuid>)
                               # send to collector -> trace_stack[-2:]
profiler.stop()                # send to collector -> trace_stack[-2:]
                               # trace_stack.pop()

profiler.stop()                # send to collector -> trace_stack[-2:]
                               # trace_stack.pop()
```

构建嵌套跟踪点的树很简单，即包含所有跟踪点的（parent_id，point_id）。

### Process of sending to collector

跟踪点包含2个消息（开始和停止）。以下消息将发送给收件人：

```
{
     "name": <point_name>-(start|stop)
     "base_id": <uuid>,
     "parent_id": <uuid>,
     "trace_id": <uuid>,
     "info": <dict>
 }

* `base_id - <uuid>` 这对于属于一个跟踪的所有跟踪点是相等的，这是为了简化从收集器检索与一个跟踪相关的所有跟踪点的过程

* `parent_id - <uuid>` 父跟踪点的 uuid

* `trace_id - <uuid>` 当前追踪点的 uuid

* `info -` 当调用 `profiler start() & stop()` 方法时，传递的包含用户信息的字典
```

### 设置 collector。

profiler 不包括跟踪点收集器。用户或者开发人员应该提供一种向收集器发送消息的方法。我们来看一个简单的例子，例子中的 collector 只是一个文件：

```
import json

from osprofiler import notifier

def send_info_to_file_collector(info, context=None):
    with open("traces", "a") as f:
        f.write(json.dumps(info))

notifier.set(send_info_to_file_collector)
```

那么现在每个 `profiler.start()` 和 `profiler.stop()` 调用中，我们将把跟踪点的信息写入跟踪文件的末尾。

#### Using OSProfiler initializer.

OSProfiler 现在包含收集跟踪数据的各种存储驱动程序。 关于要使用什么驱动程序和什么选项传递给 OSProfiler 的信息现在存储在 OpenStack 服务配置文件中。 配置的示例如下：

```
[profiler]
enabled = True
trace_sqlalchemy = True
hmac_keys = SECRET_KEY
connection_string = messaging://
```

如果提供这样的配置，OSProfiler设置可以按以下方式处理：

```
if CONF.profiler.enabled:
    osprofiler_initializer.init_from_conf(
        conf=CONF,
        context=context.get_admin_context().to_dict(),
        project="cinder",
        service=binary,
        host=host
    )
```

### Initialization of profiler.

如果 profiler 未初始化，则对 `profiler.start()` 和 `profiler.stop()` 的所有调用将被忽略。

初始化是一个非常简单的过程。

```
from osprofiler import profiler

profiler.init("SECRET_HMAC_KEY", base_id=<uuid>, parent_id=<uuid>)
```

** `SECRET_HMAC_KEY ` ** 这个参数我们待会讨论，因为这个参数牵扯到 OSprofiler 和 OpenStack 的继承。

`base_id` 和 `trace_id` 将用于在分析器中初始化 `stack_trace`。例如： `stack_trace = [base_id，trace_id]` 。

### OSProfiler CLI.

为了使终端用户更容易从CLI中使用 profiler 来工作，osprofiler 具有允许他们获取有关跟踪的信息并将其呈现方便人们读写格式的 entry point。

可用命令：

 * 帮助消息与所有可用的命令及其参数：

```
$ osprofiler -h/--help
```

* OSProfiler version:

```
$ osprofiler -v/--version
```

* 可以以 JSON（选项： - json）或 HTML（选项：--html）格式中获取分析结果：

```
$ osprofiler trace show <trace_id> --json/--html
```

* 选项--out会将osprofiler跟踪显示的结果重定向到指定的文件中：

```
$ osprofiler trace show <trace_id> --json/--html --out /path/to/file
```

* 在具有存储驱动程序（例如MongoDB（URI：mongodb：//），Messaging（URI：messaging：//）和Ceilometer（URI：ceilometer：//））的最新版本的 OSProfiler 中 - 应该设置connection-string参数：

```
$ osprofiler trace show <trace_id> --connection-string=<URI> --json/--html
```


## Integration with OpenStack

关于 OSprofiler 和 OpenStack 的集成有4个话题：

### What we should use as a centralized collector?

We decided to use [Ceilometer](https://wiki.openstack.org/wiki/Ceilometer), because:

* 它已经集成在OpenStack中，因此从所有项目向它发送通知都很简单。

* Ceilometer中有一个OpenStack API，允许我们检索与一个跟踪相关的所有消息。看看`osprofiler.parsers.ceilometer`：`get_notifications`
 
### How to setup profiler notifier?

We decided to use olso.messaging Notifier API, because:

* 所有项目都集成了 [oslo.messaging](https://pypi.python.org/pypi/oslo.messaging)

* 它是向Ceilometer发送通知是最简单的方法，请查看：`osprofiler.notifiers.messaging.Messaging：notify` 方法

* 我们不需要在项目中添加任何新的 [CONF](http://docs.openstack.org/developer/oslo.config/) 选项

### How to initialize profiler, to get one trace across all services?

要启用跨服务分析，我们实际上需要从调用者发送到被调用者（base_id＆trace_id）。所以被调用者将能够使用这些值初始化其 profiler 。

在OpenStack的情况下，2种服务之间有2种互动：

* REST API

众所周知，每个项目都有python客户端，生成适当的HTTP请求，并解析对象的响应。

这些python客户端用于2种情况：

User access -> OpenStack

Service from Project 1 would like to access Service from Project 2

所以我们需要的是：

在 python 客户端中放入带有跟踪信息的消息头（如果 profiler 被初始化）

将 [OSprofiler WSGI中间件](https://github.com/openstack/osprofiler/blob/master/osprofiler/web.py) 添加到您的服务中，这将初始化 profiler，当且仅当存在由api-paste.ini中的一个 HMAC 密钥签名的特殊跟踪头时（如果存在多个密钥，则签名过程将继续使用验证期间接受的 key）。

用于配置中间件的常用项目如下（可以在初始化中间件对象时或在设置api-paste.ini文件时提供这些项目）：

```
hmac_keys = KEY1, KEY2 (can be a single key as well)
```

其实算法有点复杂。 Python客户端还将使用传递到profiler.init的HMAC密钥（允许调用该key A）来标识跟踪信息，并且在接收时，WSGI中间件将检查它是否与其中一个HMAC密钥一起签名（wsgi服务器应该具有密钥 A，也可以具有密钥B和C），它们在api-paste.ini中指定。 这确保只有知道api-paste.ini中的HMAC密钥A的用户才能正确地初始化分析器并发送将被实际处理的跟踪信息。 这将确保发送的跟踪信息不通过 HMAC 验证将被丢弃。 NOTE: The application of many possible validation keys makes it possible to roll out a key upgrade in a non-impactful manner (by adding a key into the list and rolling out that change and then removing the older key at some time in the future).

* RPC API

RPC调用用于一个项目的服务之间的交互。众所周知，项目正在使用oslo.messaging处理RPC。这是非常好的，因为项目以类似的方式处理RPC。

所以有2个必要的更改：

在被调用方放置请求上下文跟踪信息（如果profiler被初始化）

在主叫方初始化 profiler，如果请求上下文中有跟踪信息。

跟踪被调用API的所有方法（可以通过profiler.trace_cls完成）。

### What points should be tracked by default?

我认为，对于所有项目，我们应该默认包括5种 point：

* 所有HTTP呼叫 - 帮助获取有关HTTP请求的完成情况，呼叫持续时间（服务延迟）以及请求中涉及项目的信息。

* 所有RPC调用 - 帮助了解一个项目中与不同服务相关的请求的部分持续时间。这些信息对于理解哪个服务产生瓶颈至关重要。

* 所有DB API调用 - 在某些情况下，缓慢的DB查询可能会产生瓶颈。所以跟踪在DB层中花费多少时间是非常有用的。

* All 驱动调用 - in case of nova, cinder and others we have vendor drivers. Duration

* 所有SQL请求（默认关闭，因为它产生大量流量）