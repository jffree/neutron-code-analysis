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
* sample\_default – a default string for sample config files
* deprecated\_for\_removal – 指示该选项在将来将会被抛弃
* deprecated\_reason –指示该选项将被抛弃的原因
* deprecated\_since – 指出该选项在哪一个版本中被抛弃
* mutable – True if this option may be reloaded
* advanced – 是否为高级选项



