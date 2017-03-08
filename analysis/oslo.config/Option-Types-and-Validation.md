# [Option Types and Validation](https://docs.openstack.org/developer/oslo.config/types.html)

`class oslo_config.types.Boolean(type_name='boolean value')`

布尔类型

值不区分大小写，可以使用1/0，yes / no，true / false或on / off进行设置。

type\_name– 在配置文件中展示的类型名称

`class oslo_config.types.Dict(value_type=None, bounds=False, type_name='dict value')`

字典类型

字典的键一定要是string类型，值可以为任意类型

* value\_type – 字典值的类型
* bounds – 当为真时，字典值应该被 “{”  “}” 括起来
* type\_name – 在配置文件中展示的类型名称

`class oslo_config.types.Float(min=None, max=None, type_name='floating point value')`

浮点类型

* min –最小值
* max – 最大值
* type\_name – 在配置文件中展示的类型名称

`class oslo_config.types.HostAddress(version=None, type_name='host address value')`

主机地址类型

表示有效的IP地址和有效的主机域名，包括完全限定的域名。对IP地址和有效主机名执行严格检查，根据RFC1912将opt值与相应类型匹配。

* version – IP 地址版本（4、6）
* type\_name - 在配置文件中展示的类型名称

`class oslo_config.types.Hostname(type_name='hostname value')`

主机域名类型

主机名指的是有效的DNS或主机名。它不能超过253个字符，具有大于63个字符的段，也不能以连字符开头或结尾。

* type\_name - 在配置文件中展示的类型名称

`class oslo_config.types.IPAddress(version=None, type_name='IP address value')`

IP 地址类型

* version – IP 地址版本（4、6）
* type\_name - 在配置文件中展示的类型名称

`class oslo_config.types.Integer(min=None, max=None, type_name='integer value', choices=None)`

* min – 最小值
* max – 最大值
* type\_name – 在配置文件中展示的类型名称
* choices –可选的有效值序列

`class oslo_config.types.List(item_type=None, bounds=False, type_name='list value')`

列表类型

* item\_type – 列表项类型
* bounds –为 True时，列表值应该被中括号包括
* type\_name – 在配置文件中展示的类型名称

`class oslo_config.types.MultiString(type_name='multi valued')`

多值字符串类型

`class oslo_config.types.Number(num_type, type_name, min=None, max=None, choices=None)`

基于整形和浮点类型的数字类型

* num\_type – 数字的类型（int、float）
* type\_name – 在配置文件中展示的类型名称
* min – 最小值
* max – 最大值
* choices – 可选的有效值序列

class oslo\_config.types.Port\(min=None, max=None, type\_name='port', choices=None\)

端口类型

* min – 最小端口号
* max – 最大端口号
* type\_name – 在配置文件中展示的类型名称
* choices – 可选的有效值序列

`class oslo_config.types.Range(min=None, max=None, inclusive=True, type_name='range value')`

范围类型

表示整数范围。范围由“ - ”字符的两侧的整数来标识。允许使用否定字词。单个数字也是有效范围。

* min – 最小值
* max – 最大值
* inclusive – 若右边界需要被包括在范围内则为真
* type\_name – 在配置文件中展示的类型名称

`class oslo_config.types.String(choices=None, quotes=False, regex=None, ignore_case=False, max_length=None, type_name='string value')`

字符串类型

* choices – 有效值序列
* quotes – 如果True且字符串用单引号或双引号括起来，将剥离这些引号。
* regex – 字符串必须符合的正则表达式，与choices 选项互斥
* ignore\_case – 为True时忽略大小学
* max\_length – 最大长度
* type\_name – 在配置文件中展示的类型名称

`class oslo_config.types.URI(max_length=None, schemes=None, type_name='uri value')`

* max\_length – 最大长度
* schemes – URL 的协议类型
* type\_name – 在配置文件中展示的类型名称

















































