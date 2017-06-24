# versionedobjects 之 field

field 对应着数据库里面的字段，每个 field 都对应着一个 field type，用来指定这个 field 的类型。

*oslo_versionedobject/field.py*

## `class AbstractFieldType(object)`

抽象基类，定义了 field type 必须实现的方法。

### `def coerce(self, obj, attr, value)` 

将 value 转换为一种强制的形式。

### `def from_primitive(self, obj, attr, value)`

将 value 从一种原始的形式转化为一种 object 接受的形式。

### `def to_primitive(self, obj, attr, value)`

将 value 从 object 形式转化为原始的形式。

### `def describe(self)`

对这个 field type 的描述。

### `def stringify(self, value)`

将 value 以一种简短的字符串的形式描述出来。

## `class FieldType(AbstractFieldType)`

基类，对 `AbstractFieldType` 的简单实现。

### `def get_schema(self)`

提供这个类型的概况。

## 所有可用的 field type 如下：

* `class String(FieldType)`
* `class SensitiveString(String)`
* `class VersionPredicate(String)`
* `class Enum(String)`
* `class StringPattern(FieldType)`
* `class UUID(StringPattern)`
* `class MACAddress(StringPattern)`
* `class PCIAddress(StringPattern)`
* `class Integer(FieldType)`
* `class NonNegativeInteger(FieldType)`
* `class Float(FieldType)`
* `class NonNegativeFloat(FieldType)`
* `class Boolean(FieldType)`
* `class FlexibleBoolean(Boolean)`
* `class DateTime(FieldType)`
* `class IPAddress(StringPattern)`
* `class IPV4Address(IPAddress)`
* `class IPV6Address(IPAddress)`
* `class IPV4AndV6Address(IPAddress)`
* `class IPNetwork(IPAddress)`
* `class IPV4Network(IPNetwork)`
* `class IPV6Network(IPNetwork)`
* `class CompoundFieldType(FieldType)`
* `class List(CompoundFieldType)`
* `class Dict(CompoundFieldType)`
* `class Set(CompoundFieldType)`
* `class Object(FieldType)`

## `class Field(object)`

从这里开始，我们看 field。

### `__init__`

```
    def __init__(self, field_type, nullable=False,
                 default=UnspecifiedDefault, read_only=False):
        self._type = field_type
        self._nullable = nullable
        self._default = default
        self._read_only = read_only
```

1. filed 类型
2. 是否可谓 None
3. 是否有默认值（无默认值则为 `UnspecifiedDefault`）
4. 是否为只读

### `def __repr__(self)`

```
    def __repr__(self):
        return '%s(default=%s,nullable=%s)' % (self._type.__class__.__name__, self._default, self._nullable)
```

### `def nullable(self)`

属性方法，判断该 field 是否可为空

### `def default(self)`

属性方法，获取该字段的默认值

### `def read_only(self)`

属性方法，判断该 field 是否只读

### `def _null(self, obj, attr)`

1. 若该 field 可为空，则返回 None
2. 若该 field 不可为空，但有默认值，则调用 `self._type.coerce` 获取转换后的默认值
3. 其他则会引发异常

### `def coerce(self, obj, attr, value)`

这个方法会在你为 object 的某一属性设置值的时候调用。

该方法通过调用 field type 的 `coerce` 方法实现。

### `def from_primitive(self, obj, attr, value)`

该方法通过调用 field type 的 `from_primitive` 方法实现。

### `def to_primitive(self, obj, attr, value)`

该方法通过调用 field type 的 `to_primitive` 方法实现。

### `def stringify(self, value)`

该方法通过调用 field type 的 `stringify` 方法实现。

### `def get_schema(self)`

1. 调用 field type 的 `get_schema` 方法
2. 在获取的结果中增加 field 的一些属性。

### `class AutoTypedField(Field)`

```
class AutoTypedField(Field):
    AUTO_TYPE = None

    def __init__(self, **kwargs):
        super(AutoTypedField, self).__init__(self.AUTO_TYPE, **kwargs)
```

## 所有可用的 field 如下：

* `class StringField(AutoTypedField)`
* `class SensitiveStringField(AutoTypedField)`
* `class VersionPredicateField(AutoTypedField)`
* `class BaseEnumField(AutoTypedField)`
* `class EnumField(BaseEnumField)`
* `class StateMachine(EnumField):`
* `class UUIDField(AutoTypedField)`
* `class MACAddressField(AutoTypedField)`
* `class PCIAddressField(AutoTypedField)`
* `class IntegerField(AutoTypedField)`
* `class NonNegativeIntegerField(AutoTypedField)`
* `class FloatField(AutoTypedField)`
* `class NonNegativeFloatField(AutoTypedField)`
* `class BooleanField(AutoTypedField)`
* `class FlexibleBooleanField(AutoTypedField)`
* `class DateTimeField(AutoTypedField)`
* `class DictOfStringsField(AutoTypedField)`
* `class DictOfNullableStringsField(AutoTypedField)`
* `class DictOfIntegersField(AutoTypedField)`
* `class ListOfStringsField(AutoTypedField)`
* `class DictOfListOfStringsField(AutoTypedField)`
* `class ListOfEnumField(AutoTypedField)`
* `class SetOfIntegersField(AutoTypedField)`
* `class ListOfSetsOfIntegersField(AutoTypedField)`
* `class ListOfIntegersField(AutoTypedField)`
* `class ListOfDictOfNullableStringsField(AutoTypedField)`
* `class ObjectField(AutoTypedField)`
* `class ListOfObjectsField(AutoTypedField)`
* `class IPAddressField(AutoTypedField)`
* `class IPV4AddressField(AutoTypedField)`
* `class IPV6AddressField(AutoTypedField)`
* `class IPV4AndV6AddressField(AutoTypedField)`
* `class IPNetworkField(AutoTypedField)`
* `class IPV4NetworkField(AutoTypedField)`
* `class IPV6NetworkField(AutoTypedField)`

## 其他

### `class DictProxyField(object)`

# 重点

**说明：** Object 对象类似于数据库中的记录，是可以有对应关系的（一对一，一对多），我们在 object 中称为父对象和子对象。

若父对象与子对象是一对一关系，则子对象会在父对象中占据一个 field，用 `ObjectField` 表示。

若父对象与子对象是一对多关系，则子对象会在父对象中占据一个 field，用 `ListOfObjectsField` 表示。

## `class ObjectField(AutoTypedField)`

```
class ObjectField(AutoTypedField):
    def __init__(self, objtype, subclasses=False, **kwargs):
        self.AUTO_TYPE = Object(objtype, subclasses)
        self.objname = objtype
        super(ObjectField, self).__init__(**kwargs)
```

## `class ListOfObjectsField(AutoTypedField)` 

```
class ListOfObjectsField(AutoTypedField):
    def __init__(self, objtype, subclasses=False, **kwargs):
        self.AUTO_TYPE = List(Object(objtype, subclasses))
        self.objname = objtype
        super(ListOfObjectsField, self).__init__(**kwargs)
```

## `class Object(FieldType)`

### ``

