# debtcollector

一系列Python弃用模式和策略，帮助您以非破坏性的方式收集您的技术过失。

**注意：**应该注意的是，尽管它的设计与OpenStack集成在一起，而且目前的大部分集成是为了在任何项目中普遍可用的。

## 安装

```
$ pip install debtcollector
```

```
$ mkvirtualenv debtcollector
$ pip install debtcollector
```

## API

### Helpers

#### `debtcollector.deprecate(prefix, postfix=None, message=None, version=None, removal_version=None, stacklevel=3, category=<type 'exceptions.DeprecationWarning'>)`

帮助弃用某些用来生成的消息格式的东西。

* Parameters:	
 1. `prefix` – 前缀字符串用作输出消息的前缀
 2. `postfix` – postfix字符串用作输出消息的后缀
 3. `message` – 消息字符串用作废弃消息的结束内容
 4. `version` – 版本字符串（表示此次 deprecation 创建的版本）
 5. `removal_version` – 版本字符串（表示此删除将被删除的版本）;一个'？'字符串表示将在未来的未知版本中被删除
 6. `stacklevel` – 在warnings.warn（）函数中使用的stacklevel来定位用户代码在warnings.warn（）调用中的位置
 7. `category` – 要使用的警告类别，如果没有提供，默认为DeprecationWarning

### Moves

#### `debtcollector.moves.moved_function(new_func, old_func_name, old_module_name, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

弃用已移至其他位置的功能。

这会为 `new_func` 产生一个包装器，在调用时会发出一个弃用警告。警告信息将包括获取 function 的新位置。

#### `class debtcollector.moves.moved_read_only_property(old_name, new_name, version=None, removal_version=None, stacklevel=3, category=None)`

Bases: object

只读属性的描述符移动到另一个位置。

这可以像 `@property` 描述符一样工作，但可以取代它并用来提供相同的功能，并且还会与 `warnings` 模块进行交互以在访问属性时发出警告，以便这些属性的用户可以知道之前的只读属性 `位置/名称` 已移动到另一个 `位置/名称`。

* Parameters:	
 1. `old_name` – 旧属性的 location/name
 2. `new_name` – 新属性的 location/name
 3. `version` – 版本字符串（表示此次 deprecation 创建的版本）
 4. `removal_version` – 版本字符串（表示此删除将被删除的版本）;一个'？'字符串表示将在未来的未知版本中被删除
 5. `stacklevel` – 在 `warnings.warn()` 函数中使用的stacklevel来定位用户代码在 `warnings.warn()` 调用中的位置（默认为3）
 6. `category` – 要使用的警告类别，如果没有提供，默认为DeprecationWarning

#### `debtcollector.moves.moved_method(new_method_name, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

装饰一个实例方法，这个实例方法已经被移动到另一个位置。

#### `debtcollector.moves.moved_property(new_attribute_name, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

装饰一个实例属性，这个实例属性已经被移动到另一个位置。

#### `debtcollector.moves.moved_class(new_class, old_class_name, old_module_name, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

装饰一个类，这个类已经被移动到另一个位置。

这将创建一个 *new-old* 类型，在弃用期内可以被继承使用。当旧位置的类被初始化时，这将发出警告，告诉现在用于替代旧类的新类的位置的改进。

### Renames

#### `debtcollector.renames.renamed_kwarg(old_name, new_name, message=None, version=None, removal_version=None, stacklevel=3, category=None, replace=False)`

Decorates a kwarg accepting function to deprecate a renamed kwarg.

### Removals

#### `class debtcollector.removals.removed_property(fget=None, fset=None, fdel=None, doc=None, stacklevel=3, category=<type 'exceptions.DeprecationWarning'>, version=None, removal_version=None, message=None)`

Bases: object

用来废弃属性的属性装饰器。

这可以像 `@property` 描述符一样工作，但可以取代它并用来提供相同的功能，并且还会与 `warnings` 模块进行交互以在访问属性时发出警告，以便在访问，设置和/或删除属性时发出警告。

* Parameters:	
 1. `message` – 用作结束废弃消息内容的字符串
 2. `version` – 版本字符串（表示此次 deprecation 创建的版本）
 3. `removal_version` – 版本字符串（表示此删除将被删除的版本）;一个'？'字符串表示将在未来的未知版本中被删除
 4. `stacklevel` – 在 `warnings.warn()` 函数中使用的stacklevel来定位用户代码在 `warnings.warn()` 调用中的位置（默认为3）
 5. `category` – 要使用的警告类别，如果没有提供，默认为`DeprecationWarning`

#### `debtcollector.removals.remove(f=None, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

装饰函数，方法或类以发出废弃警告

由于wrapt库（和python）本身的限制，如果这适用于元类的子类，那么它可能不会按预期工作。 更多信息可以在bug＃1520397找到，看看这种情况是否会影响你对这个通用装饰器的使用，对于这个具体的场景，请改用 `remove_class()`。

* Parameters:	
 1. message (str) – 要包含在废弃警告中的消息
 2. `version` – 版本字符串（表示此次 deprecation 创建的版本）
 3. `removal_version` – 版本字符串（表示此删除将被删除的版本）;一个'？'字符串表示将在未来的未知版本中被删除
 4. `stacklevel` – 在 `warnings.warn()` 函数中使用的stacklevel来定位用户代码在 `warnings.warn()` 调用中的位置
 5. `category` – 要使用的警告类别，如果没有提供，默认为`DeprecationWarning`

#### `debtcollector.removals.removed_kwarg(old_name, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

Decorates a kwarg accepting function to deprecate a removed kwarg.

#### `debtcollector.removals.removed_class(cls_name, replacement=None, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

Decorates a class to denote that it will be removed at some point.

#### `debtcollector.removals.removed_module(module, replacement=None, message=None, version=None, removal_version=None, stacklevel=3, category=None)`

Helper to be called inside a module to emit a deprecation warning

* Parameters:	
 1. `replacment (str)` – 取消模块的任何潜在替换的位置（或信息）（如果适用）
 2.  `message (str)` – 要包含在废弃警告中的消息
 3. `version` – 版本字符串（表示此次 deprecation 创建的版本）
 4. `removal_version` – 版本字符串（表示此删除将被删除的版本）;一个'？'字符串表示将在未来的未知版本中被删除
 5. `stacklevel` – 在 `warnings.warn()` 函数中使用的stacklevel来定位用户代码在 `warnings.warn()` 调用中的位置
 6. `category` – 要使用的警告类别，如果没有提供，默认为`DeprecationWarning`

### Fixtures

#### `class debtcollector.fixtures.disable.DisableFixture`

Bases: `fixtures.fixture.Fixture`

禁止 debtcollector 出发报警。

这不会禁用其他库发出的警告调用。

可以像下面一样使用：

```
from debtcollector.fixtures import disable

with disable.DisableFixture():
    <some code that calls into depreciated code>
``

## [Examples](https://docs.openstack.org/developer/debtcollector/examples.html)