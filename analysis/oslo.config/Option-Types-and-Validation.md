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
*  type\_name - 在配置文件中展示的类型名称

`class oslo_config.types.Hostname(type_name='hostname value')`

主机域名类型

主机名指的是有效的DNS或主机名。它不能超过253个字符，具有大于63个字符的段，也不能以连字符开头或结尾。

* type\_name - 在配置文件中展示的类型名称

`class oslo_config.types.IPAddress(version=None, type_name='IP address value')`

IP 地址类型

* version – IP 地址版本（4、6）
*  type\_name - 在配置文件中展示的类型名称

`class oslo_config.types.Integer(min=None, max=None, type_name='integer value', choices=None)`

* min – 最小值
* max – 最大值
* type\_name – 在配置文件中展示的类型名称
* choices –可选的有效值序列

`class oslo_config.types.List(item_type=None, bounds=False, type_name='list value')`



























