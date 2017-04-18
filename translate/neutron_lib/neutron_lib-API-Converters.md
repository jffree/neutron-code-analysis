# API Converters

REST API属性的定义可以包括转换方法，以帮助规范用户输入或将输入转换为可以使用的形式。

## 定义一个 Converter Method

按照惯例，名称应以 `convert_to_` 开头，并且将为要转换的数据设定一个参数。 该方法应该返回转换后的数据（如果输入为None，并且没有进行转换，则可以使用该方法返回的隐式None）。 如果转换是不可能的，则应该引发一个 `InvalidInput` 异常，指出什么是错误的。 例如，这里将各种用户输入转换为布尔值。

```
def convert_to_boolean(data):
     if isinstance(data, six.string_types):
         val = data.lower()
         if val == "true" or val == "1":
             return True
         if val == "false" or val == "0":
             return False
     elif isinstance(data, bool):
         return data
     elif isinstance(data, int):
         if data == 0:
             return False
         elif data == 1:
             return True
     msg = _("'%s' cannot be converted to boolean") % data
     raise n_exc.InvalidInput(error_message=msg)
```

## 使用验证

在客户端代码中，转换可以在REST API定义中使用，方法名称作为属性的 `convert_to` 键的值。例如：

```
'admin_state_up': {'allow_post': True, 'allow_put': True,
                   'default': True,
                   'convert_to': conversions.convert_to_boolean,
                   'is_visible': True},
```

这里，`admin_state_up` 是一个布尔值，所以转换器用于取得用户的（字符串）输入并将其转换为布尔值。

## 测试验证器

做正确的事情，并确保您为添加的任何转换器创建了一个单元测试，以验证其是否按预期工作。

## IPv6规范地址格式化程序

有几种方法来显示IPv6地址，这可能会给用户，工程师和运营商带来很多困惑。 为了减少编写IPv6地址的多方面风格的影响，建议以 Neutron 规范格式保存 IPv6 地址。

如果用户传入IPv6地址，将以规范格式保存。

The full document is found at : http://tools.ietf.org/html/rfc5952