# neutron 中的 osprofiler 的使用

## osprofiler 在 neutron 的三个位置被初始化：

* 在启动 neutron-server 时：

_neutron/service.py_

```
class NeutronApiService(WsgiService):
    """Class for neutron-api service."""
    def __init__(self, app_name):
        profiler.setup('neutron-server', cfg.CONF.host)
        super(NeutronApiService, self).__init__(app_name)
```

* 在启动 linuxbridge agent 时：

_neutron/plugins/ml2/drivers/linuxbridge/agent/linuxbridge\_neutron\_agent.py_

```
def main():
    ....

    setup_profiler.setup("neutron-linuxbridge-agent", cfg.CONF.host)
```

* 在启动 mech\_sriov agent 时：

_neutron/plugins/ml2/drivers/mech\_sriov/agent/sriov\_nic\_agent.py_

```
def main():
    ....

    setup_profiler.setup("neutron-sriov-nic-agent", cfg.CONF.host)
```

* 在启动 openvswitch agent 时：

_neutron/plugins/ml2/drivers/openvswitch/agent/main.py_

```
def main():
    ....

    profiler.setup("neutron-ovs-agent", cfg.CONF.host)
```

## Neutron 中 OSProfiler 初始化的具体实现：

_neutron/common/profiler.py_

```
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
import osprofiler.notifier
from osprofiler import opts as profiler_opts
import osprofiler.web

from neutron._i18n import _LI

CONF = cfg.CONF
profiler_opts.set_defaults(CONF)
LOG = logging.getLogger(__name__)


def setup(name, host='0.0.0.0'):  # nosec
    """Setup OSprofiler notifier and enable profiling.

    :param name: name of the service, that will be profiled
    :param host: host (either host name or host address) the service will be
                 running on. By default host will be set to 0.0.0.0, but more
                 specified host name / address usage is highly recommended.
    """
    if CONF.profiler.enabled:
        _notifier = osprofiler.notifier.create(
            "Messaging", oslo_messaging, {},
            oslo_messaging.get_transport(CONF), "neutron", name, host)
        osprofiler.notifier.set(_notifier)
        osprofiler.web.enable(CONF.profiler.hmac_keys)
        LOG.info(_LI("OSProfiler is enabled.\n"
                     "Traces provided from the profiler "
                     "can only be subscribed to using the same HMAC keys that "
                     "are configured in Neutron's configuration file "
                     "under the [profiler] section.\n To disable OSprofiler "
                     "set in /etc/neutron/neutron.conf:\n"
                     "[profiler]\n"
                     "enabled=false"))
```

1. `profiler_opts.set_defaults(CONF)` 添加关于 osprofiler 的配置选项

2. `setup` 方法做了具体的初始化的事情：

   1. 创建一个通知器（收集器） `_notifier`

   2. 为 osprofiler 设定这个通知器

   3. Enable middleware.

   4. LOG 输出

## 通知器（收集器） `_notifier` 的创建

详细的可以自己看代码，我这里只介绍大概。

osprofiler 定义了一系列的驱动后端，在 _osprofiler/drivers_ 目录下，每个模块即为一个可用的驱动后端。

`"Messaging"` 就是来获取这些驱动后端 `class Messaging` \(_osprofiler/drivers/messaging.py_\)

`oslo_messaging, {}, oslo_messaging.get_transport(CONF), "neutron", name, host` 则是传递给这个驱动后端 `Messaging` 的初始化参数。

跟踪进去就可以发现这是就是将 `oslo_messaging.Notifer` 作为真正消息处理的后端，并为其做了初始化。

## 命令行使用

我还没有找到如何使用 osprofiler 的命令，也因为我的 devstack 没有安装 ceilometer 无法尝试，不过有一篇 [osprofiler 在 cinder 中应用](http://www.cnblogs.com/sting2me/p/4393018.html) 的文章，大家可以参考。

