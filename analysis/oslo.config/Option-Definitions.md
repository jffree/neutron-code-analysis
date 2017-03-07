# 定义选项

`class oslo_config.cfg.Opt(name, type=None, dest=None, short=None, default=None, positional=False, metavar=None, help=None, secret=False, required=False, deprecated_name=None, deprecated_group=None, deprecated_opts=None, sample_default=None, deprecated_for_removal=False, deprecated_reason=None, deprecated_since=None, mutable=False, advanced=False)`

定义选项的基类。

唯一必须的参数是 name，但是通常提供 `default `和 `help `信息。

* name – 选项名称
* type – 选项类型（必须是一个可调用的对象，用来返回选项值）
* dest – the name of the corresponding ConfigOpts property
* short – a single character CLI option name
* default – the default value of the option
* positional – True if the option is a positional CLI argument
* metavar – the option argument to show in –help
* help – an explanation of how the option is used
* secret – true if the value should be obfuscated in log output
* required – true if a value must be supplied for this option
* deprecated\_name – deprecated name option. Acts like an alias
* deprecated\_group – the group containing a deprecated alias
* deprecated\_opts – list of DeprecatedOpt
* sample\_default – a default string for sample config files
* deprecated\_for\_removal – indicates whether this opt is planned for removal in a future release
* deprecated\_reason – indicates why this opt is planned for removal in a future release. Silently ignored if deprecated\_for\_removal is False
* deprecated\_since – indicates which release this opt was deprecated in. Accepts any string, though valid version strings are encouraged. Silently ignored if deprecated\_for\_removal is False
* mutable – True if this option may be reloaded
* advanced – a bool True/False value if this option has advanced usage and is not normally used by the majority of users









