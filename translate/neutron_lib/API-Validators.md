# API Validators

对于REST API，属性可能定义了自定义验证器。 每个验证器都将有一个执行验证的方法和一个类型定义字符串，以便可以引用验证器。

## 定义一个验证器方法

验证方法将具有要验证的数据的位置参数，并且可能具有可在验证期间使用的其他（可选）关键字参数。 该方法必须处理任何异常，并返回None（成功）或指示验证失败消息的i18n字符串。 按照惯例，方法名前缀为 `validate_`，然后包含数据类型。 例如：

```
def validate_uuid(data, valid_values=None):
   if not uuidutils.is_uuid_like(data):
       msg = _("'%s' is not a valid UUID") % data
       LOG.debug(msg)
       return msg
```

有一个验证字典将方法映射到可在REST API定义中引用的验证类型。 字典中的条目将如下所示：

```
'type:uuid': validate_uuid,
```

## 使用验证器

在客户端代码中，验证器可以通过使用验证器的字典键在REST API中使用。 例如：

```
RESOURCE_ATTRIBUTE_MAP = {
    NETWORKS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': NAME_MAX_LEN},
                 'default': '', 'is_visible': True},
```

这里，网络资源具有带有UUID验证器的 `id` 属性，如 `validate` 键所示，该键包含具有 `type：uuid` 键的字典。

验证器的任何附加参数都可以指定为字典条目的值（在这种情况下，`NAME` 属性中的 NAME_MAX_LEN 不使用字符串验证器）。在IP版本属性中，可以有一个验证器定义如下：

```
'ip_version': {'allow_post': True, 'allow_put': False,
               'convert_to': conversions.convert_to_int,
               'validate': {'type:values': [4, 6]},
               'is_visible': True},
```

这里，`validate_values()` 方法将获取值列表作为可以为此属性指定的允许值。

## 测试验证器

做正确的事情，并确保您为添加的任何验证器创建了一个单元测试，以验证它是否按预期工作，即使是简单的验证器。