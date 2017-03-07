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

选项可以被声明为必须的，若是没有为其提供值将会报错

```
opts = [
    cfg.StrOpt('service_name', required=True),
    cfg.StrOpt('image_id', required=True),
    ...
]
```

选项也可以被声明为保密的，这些选项的值将不会在日志中体现

```
opts = [
   cfg.StrOpt('s3_store_access_key', secret=True),
   cfg.StrOpt('s3_store_secret_key', secret=True),
   ...
]
```

### 字典类型选项：

若是需要用书提供字典（键值对）类型的选项，那么你可以使用 `DictOpt`:

```
opts = [
    cfg.DictOpt('foo',
                default={})
]
```

那么，用户可以在配置文件中写成下面的方式：

```
[DEFAULT]
foo = k1:v1,k2:v2
```

### 全局ConfigOpts

该模块提供了一个ConfigOpts的全局实例，以便在Openstack统一使用。

```
from oslo_config import cfg

opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0'),
    cfg.PortOpt('bind_port', default=9292),
]

CONF = cfg.CONF
CONF.register_opts(opts)

def start(server, app):
    server.start(app, CONF.bind_port, CONF.bind_host)
```

命令行位置参数

通过 positional 参数可声明一个命令行位置参数

```
>>> conf = cfg.ConfigOpts()
>>> conf.register_cli_opt(cfg.MultiStrOpt('bar', positional=True))
True
>>> conf(['a', 'b'])
>>> conf.bar
['a', 'b']
```

子解析器

继承自 argpparse 中的 sub-parse 的概念（将多个命令组合进一个程序中，使用子解析器来处理命令行的每个部分。），使用SubCommandOpt来实现。

```
#在 argparse中的例子
ArgumentParser.add_subparsers([title][, description][, prog][, parser_class][, action][, option_string][, dest][, help][, metavar])
>>> # create the top-level parser
>>> parser = argparse.ArgumentParser(prog='PROG')
>>> parser.add_argument('--foo', action='store_true', help='foo help')
>>> subparsers = parser.add_subparsers(help='sub-command help')
>>>
>>> # create the parser for the "a" command
>>> parser_a = subparsers.add_parser('a', help='a help')
>>> parser_a.add_argument('bar', type=int, help='bar help')
>>>
>>> # create the parser for the "b" command
>>> parser_b = subparsers.add_parser('b', help='b help')
>>> parser_b.add_argument('--baz', choices='XYZ', help='baz help')
>>>
>>> # parse some argument lists
>>> parser.parse_args(['a', '12'])
Namespace(bar=12, foo=False)
>>> parser.parse_args(['--foo', 'b', '--baz', 'Z'])
Namespace(baz='Z', foo=True)
```

```
>>> def add_parsers(subparsers):
...     list_action = subparsers.add_parser('list')
...     list_action.add_argument('id')
...
>>> conf = cfg.ConfigOpts()
>>> conf.register_cli_opt(cfg.SubCommandOpt('action', handler=add_parsers))
True
>>> conf(args=['list', '10'])
>>> conf.action.name, conf.action.id
('list', '10')
```

### 高级选项

如果需将选项标记为高级，指示该选项通常不被大多数用户使用，并且可能对稳定性和/或性能有重大影响，请使用此选项：

```
from oslo_config import cfg

opts = [
    cfg.StrOpt('option1', default='default_value',
                advanced=True, help='This is help '
                'text.'),
    cfg.PortOpt('option2', default='default_value',
                 help='This is help text.'),
]

CONF = cfg.CONF
CONF.register_opts(opts)
```

这将会导致该选项被推送到命名空间的底部，并在示例文件中标记为高级，并带有关于可能的效果的符号：

```
[DEFAULT]
...
# This is help text. (string value)
# option2 = default_value
...
<pushed to bottom of section>
...
# This is help text. (string value)
# Advanced Option: intended for advanced users and not used
# by the majority of users, and might have a significant
# effect on stability and/or performance.
# option1 = default_value
```

### 弃用选项

如果要重命名一些选项，或者它们移动到另一个组或完全删除，可以在 Opt的构造函数中使用deprecated\_name，deprecated\_group和deprecated\_for\_removal参数进行声明：

```
from oslo_config import cfg

conf = cfg.ConfigOpts()

opt_1 = cfg.StrOpt('opt_1', default='foo', deprecated_name='opt1')
opt_2 = cfg.StrOpt('opt_2', default='spam', deprecated_group='DEFAULT')
opt_3 = cfg.BoolOpt('opt_3', default=False, deprecated_for_removal=True)

conf.register_opt(opt_1, group='group_1')
conf.register_opt(opt_2, group='group_2')
conf.register_opt(opt_3)

conf(['--config-file', 'config.conf'])

assert conf.group_1.opt_1 == 'bar'
assert conf.group_2.opt_2 == 'eggs'
assert conf.opt_3
```

假定配置文件的内容如下：

```
[group_1]
opt1 = bar

[DEFAULT]
opt_2 = eggs
opt_3 = True
```

该脚本将成功，但会记录有关给定的已弃用选项的三个相应的警告。

还有`deprecated_reason`和`deprecated_since`参数，用于指定有关弃用的一些其他信息。

所有提及的参数可以以任何组合混合在一起。





























