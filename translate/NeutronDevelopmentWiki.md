## API Extensions

API Extension 允许插件扩展 Neutron API 以便公开更多信息。 该信息可能需要实现特定于某个插件的高级功能，或者在将其纳入官方 Neutron API 之前将其展现出来。

我们强烈地认为，为官方 API “提出” 新功能的正确方法是首先将其作为扩展。 代码是一个非常具体的定义，编写代码和实现代码通常会暴露出仅仅是对API讨论太抽象而没有的重要细节。

* Creating Extensions:

 * 扩展文件应放置在扩展文件夹中：*neutron/extensions*。

 * 扩展文件应该具有与文件名相同名称的类。这个类应该实现扩展框架的所有要求。有关详细信息，请参阅 *neutron/api/extensions.py* 中的 `ExtensionDescriptor` 类。

 * 要停止扩展文件夹中的文件作为扩展加载，文件名应以 `_` 开头。 有关扩展文件的示例，请查看 *neutron/tests/unit/extensions/foxinsocks.py* 中的 `Foxinsocks` 类。 在 *neutron/tests/unit/api/test_extensions.py* 中单元测试列出了在扩展可以使用的所有方法。

* 将插件与扩展相关联

 * 插件可以通过 `supported_extension_aliases` 属性来发布其支持的所有扩展。例如：

```
      class SomePlugin:
        ...
        supported_extension_aliases = ['extension1_alias',
                                     'extension2_alias',
                                     'extension3_alias']
      Any extension not in this list will not be loaded for the plugin
```

* 插件的扩展接口（可选）。扩展可以实现 `get_plugin_interface` 方法来强制插件有必须支持的接口。有关示例，请参阅 *foxinsocks.py* 中的 `FoxInSocksPluginInterface` 。

### Neutron 中的三种 extension

1. Resources 为 API 引入了一个新的 entry。在 neutron 方面，当前的实体是 networks 和  	ports。

2. Action extensions 往往作用于资源上的一个“动词”。 例如，在Nova中，有一个 server 资源和对该服务器资源的 rebuild action：http://docs.openstack.org/cactus/openstack-compute/developer/openstack-compute-api-1.1/content/Rebuild_Server-d1e3538.html#d2278e1430。 核心Neutron API并没有真正使用 action 作为核心API的一部分，但 extension 可以。

3. Request extensions 允许向现有请求对象添加新值。例如，如果您正在通过 POST 动作来创建 server，但是想要为服务器对象添加一个新的 `widgetType` 属性。

查看Foxinsox，以及使用它的测试可以在这里有所帮助：*neutron/tests/unit/extensions/foxinsocks.py* 以及 *neutron/tests/unit/api/test_extensions.py*。

您还可以查看 *neutron/extensions* 的其他扩展，或者 *nova/api/openstack/compute/contrib/* 中的nova扩展（这些记录在这里：http://nova.openstack.org/api_ext/index.html）

通常最好的办法是找到另外一个扩展名，做一些类似于你正在做的事情，然后把它作为一个模板。