# 定义选项

`class oslo_config.cfg.Opt(name, type=None, dest=None, short=None, default=None, positional=False, metavar=None, help=None, secret=False, required=False, deprecated_name=None, deprecated_group=None, deprecated_opts=None, sample_default=None, deprecated_for_removal=False, deprecated_reason=None, deprecated_since=None, mutable=False, advanced=False)`

定义选项的基类。

唯一必须的参数是 name，但是通常提供 `default`和 `help`信息。

* name – 选项名称
* type – 选项类型（必须是一个可调用的对象，用来返回选项值）
* dest – the name of the corresponding ConfigOpts property
* short – 一个单字母的命令行选项名称（缩写）
* default – 选项的默认值
* positional – 该选项是否为一个命令行位置选项
* metavar – 在 -help后展示的信息
* help – 帮助信息
* secret –是否为秘密选项，不在日志文件中展示
* required – 是否为必须选项
* deprecated\_name – 被放弃的名称，类似于重命名
* deprecated\_group –被放弃的组名称
* deprecated\_opts – list of DeprecatedOpt
* sample\_default – 在配置文件中的默认值
* deprecated\_for\_removal – 指示该选项在将来将会被抛弃
* deprecated\_reason –指示该选项将被抛弃的原因
* deprecated\_since – 指出该选项在哪一个版本中被抛弃
* mutable – True if this option may be reloaded
* advanced – 是否为高级选项

`class oslo_config.cfg.StrOpt(name, choices=None, quotes=None, regex=None, ignore_case=None, max_length=None, **kwargs)`

string或[`oslo_config.types.String`](https://docs.openstack.org/developer/oslo.config/types.html#oslo_config.types.String) 类型的选项

* name – 选项名称
* choices – 可选的有效值序列
* quotes –此值为True，且字符串被单引号或双引号括起来时，将剥去这些引号
* regex – 可选的正则表达式，提供的选项值必须与此匹配
* ignore\_case –若果为 True的话将会忽略 choices 和 quotes的大小写差异
* max\_length – 选项值的最大长度
* \*\*kwargs – 传递给 Opt 的其他可选参数

`class oslo_config.cfg.BoolOpt(name, **kwargs)`

布尔类型的选项

在命令行中使用 –optname 或–nooptname将选项设定为 True 或 False

在配置文件中，布尔值使用布尔类型

* name – 选项名称
* \*\*kwargs – 传递给 Opt 的其他可选参数

`class oslo_config.cfg.IntOpt(name, min=None, max=None, **kwargs)`

整形或[`oslo_config.types.Integer`](https://docs.openstack.org/developer/oslo.config/types.html#oslo_config.types.Integer)类型的选项

* name – 选项名称
* min – 参数可选择的最小值
* max – 参数可选择的最大值
* \*\*kwargs – 传递给 Opt 的其他可选参数

`class oslo_config.cfg.FloatOpt(name, min=None, max=None, **kwargs)`

列表（字符串）或[`oslo_config.types.List`](https://docs.openstack.org/developer/oslo.config/types.html#oslo_config.types.List)类型的选项

* name – 选项名称
* item\_type – 列表项类型
* bounds –若为 True，则值应该被 '\[' '\]' 括起来
* \*\*kwargs – 传递给 Opt 的其他可选参数

`class oslo_config.cfg.DictOpt(name, **kwargs)`

字典（字符串）、[`oslo_config.types.Dict`](https://docs.openstack.org/developer/oslo.config/types.html#oslo_config.types.Dict)类型的选项

* name – 选项名称

* \*\*kwargs – 传递给 Opt 的其他可选参数

`class oslo_config.cfg.MultiOpt(name, item_type, **kwargs)`

多值选项

选项值是一个列表，包含有所有的值。

* name – 选项名称
* item\_type – 列表项类型
* \*\*kwargs – 传递给 Opt 的其他可选参数

例如：

```
cfg.MultiOpt('foo',
             item_type=types.Integer(),
             default=None,
             help="Multiple foo option")
```

在命令行中使用`--foo=1--foo=2，那么 cfg.CONF.foo将会是[1,2]`

  






















