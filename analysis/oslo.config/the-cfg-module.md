cfg 模块

配置选项可以在命令行或配置文件中设置。

选项都是通过 [Opt ](https://docs.openstack.org/developer/oslo.config/opts.html#oslo_config.cfg.Opt)或其子类来定义的：

```py
from oslo_config import cfg
from oslo_config import types

PortType = types.Integer(1, 65535)

common_opts = [
    cfg.StrOpt('bind_host',
               default='0.0.0.0',
               help='IP address to listen on.'),
    cfg.Opt('bind_port',
            type=PortType,
            default=9292,
            help='Port number to listen on.')
]

```







