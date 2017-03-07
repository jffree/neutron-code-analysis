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

选项类型：

选项可以在 `Opt`构造函数的 `type`参数中定义其类型。`type`参数是一个可调用对象，它接受一个字符串，并返回该特定类型的值，或者如果该值无法转换，则引发`ValueError`。

为了方便，[`oslo_config.cfg`](https://docs.openstack.org/developer/oslo.config/cfg.html#module-oslo_config.cfg) 预定义了包含特定类型的子类。

例如，[`oslo_config.cfg.MultiOpt`](https://docs.openstack.org/developer/oslo.config/opts.html#oslo_config.cfg.MultiOpt\)通过 `item_type `参数来定义值的类型。为了方便[`oslo_config.cfg.MultiStrOpt`]\(https://docs.openstack.org/developer/oslo.config/opts.html#oslo_config.cfg.MultiStrOpt\)类即使将 item_type 参数设为[`oslo_config.types.MultiString`]\(https://docs.openstack.org/developer/oslo.config/types.html#oslo_config.types.MultiString\)的[`oslo_config.cfg.MultiOpt`]\(https://docs.openstack.org/developer/oslo.config/opts.html#oslo_config.cfg.MultiOpt)的子类。

以下示例使用子类定义选项：

```py
enabled_apis_opt = cfg.ListOpt('enabled_apis',
                               default=['ec2', 'osapi_compute'],
                               help='List of APIs to enable by default.')

DEFAULT_EXTENSIONS = [
    'nova.api.openstack.compute.contrib.standard_extensions'
]
osapi_compute_extension_opt = cfg.MultiStrOpt('osapi_compute_extension',
                                              default=DEFAULT_EXTENSIONS)
```

### 注册选项

选项在使用前必须注册到配置管理器：

```
class ExtensionManager(object):

    enabled_apis_opt = cfg.ListOpt(...)

    def __init__(self, conf):
        self.conf = conf
        self.conf.register_opt(enabled_apis_opt)
        ...

    def _load_extensions(self):
        for ext_factory in self.conf.osapi_compute_extension:
            ....
```

一种常见的使用方法是

```
opts = ...

def add_common_opts(conf):
    conf.register_opts(opts)

def get_bind_host(conf):
    return conf.bind_host

def get_bind_port(conf):
    return conf.bind_port
```

有的选项可以通过命令行来使用，这些选线在被解析之前同样需要注册到配置管理器（为了help信息和 CLI 参数检查 ）

```
cli_opts = [
    cfg.BoolOpt('verbose',
                short='v',
                default=False,
                help='Print more verbose output.'),
    cfg.BoolOpt('debug',
                short='d',
                default=False,
                help='Print debugging output.'),
]

def add_common_opts(conf):
    conf.register_cli_opts(cli_opts)
```

### 加载配置文件

配置管理器有两个默认定义的CLI选项，-config-file和-config-dir：

```py
class ConfigOpts(object):

    def __call__(self, ...):

        opts = [
            MultiStrOpt('config-file',
                    ...),
            StrOpt('config-dir',
                   ...),
        ]

        self.register_cli_opts(opts)
```

oslo\_config.iniparser用于解析配置文件，若配置文件未声明，则一系列默认的文件将被使用，例如glance-api.conf、glance-common.conf。

```
glance-api.conf:
  [DEFAULT]
  bind_port = 9292

glance-common.conf:
  [DEFAULT]
  bind_host = 0.0.0.0
```

配置文件中的每一行不得以空格开头。在配置文件中可以用 **\# **和 **;** 来表示注释行。无论是命令行选项还是配置文件选项都会按照顺序解析。对于多次出现的同一选项来说，后面的值将覆盖前面的值。

同一配置目录中的配置文件的顺序由其文件名的字母排序顺序定义。

CLI参数和配置文件的解析是通过调用配置管理器来启动的，例如：

```
conf = cfg.ConfigOpts()
conf.register_opt(cfg.BoolOpt('verbose', ...))
conf(sys.argv[1:])
if conf.verbose:
    ...
```

### 选项组：

选项在注册时，可以声明属于一个组：

```
rabbit_group = cfg.OptGroup(name='rabbit',
                            title='RabbitMQ options')

rabbit_host_opt = cfg.StrOpt('host',
                             default='localhost',
                             help='IP/hostname to listen on.'),
rabbit_port_opt = cfg.PortOpt('port',
                              default=5672,
                              help='Port number to listen on.')

def register_rabbit_opts(conf):
    conf.register_group(rabbit_group)
    # options can be registered under a group in either of these ways:
    conf.register_opt(rabbit_host_opt, group=rabbit_group)
    conf.register_opt(rabbit_port_opt, group='rabbit')
```

如果组除名称之外不需要别的属性，则不需要显式地注册组，例如：

```
def register_rabbit_opts(conf):
    # The group will automatically be created, equivalent calling::
    #   conf.register_group(OptGroup(name='rabbit'))
    conf.register_opt(rabbit_port_opt, group='rabbit')
```

若是在注册选项是，没有声明所属组，则会将其归为 `DEFAULT`组

```
glance-api.conf:
  [DEFAULT]
  bind_port = 9292
  ...

  [rabbit]
  host = localhost
  port = 5672
  use_ssl = False
  userid = guest
  password = guest
  virtual_host = /
```

命令行选项将自动带有组名称作为前缀：

```
--rabbit-host localhost --rabbit-port 9999
```

### 在你的代码中访问选项值

属于默认组的选项值可通过配置管理器直接访问，其他的可通过组名进行访问。

```
server.start(app, conf.bind_port, conf.bind_host, conf)

self.connection = kombu.connection.BrokerConnection(
    hostname=conf.rabbit.host,
    port=conf.rabbit.port,
    ...)
```

### 选项插值

选项的值可以被其他选项值引用：

```
opts = [
    cfg.StrOpt('state_path',
               default=os.path.join(os.path.dirname(__file__), '../'),
               help='Top-level directory for maintaining nova state.'),
    cfg.StrOpt('sqlite_db',
               default='nova.sqlite',
               help='File name for SQLite.'),
    cfg.StrOpt('sql_connection',
               default='sqlite:///$state_path/$sqlite_db',
               help='Connection string for SQL database.'),
]
```

### 其他特殊说明























