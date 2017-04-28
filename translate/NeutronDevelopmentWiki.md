# [NeutronDevelopment Wiki](https://wiki.openstack.org/wiki/NeutronDevelopment)

## Developing a Neutron Plugin

如果您尝试在 OpenStack 使用新的网络交换技术，那么您可能希望开发一个Neutron插件。那么你来到正确的地方。

### What is a Neutron Plugin?

Neutron 公开了一系列逻辑 API 来定义网络，以让来自其他 OpenStack 服务（例如，来自Nova VM的vNIC）的设备实现连接。 使用API描述的逻辑连接必须转换为虚拟或物理交换机上的实际配置。 这是Neutron插件所要做的事情。Neutron插件能够与一个或多个类型的交换机通话，并根据API调用动态重新配置交换机。

### What Code Do I Need to Write

Neutron 代码库有一个python API，您若是想要实现一个 Neutron 插件，则必须实现这一组API调用。源代码请看 *neutron/neutron_plugin_base.py*。

如果您选择围绕着 SQL 数据库来构建插件，代码库提供一些有用的 sqlalchemy 绑定来存储逻辑API实体（网络，端口）。

一个插件通常由以下代码组成：

* 存储有关当前逻辑网络配置的信息（例如，SQL数据库）

* 确定并存储有关逻辑模型到物理网络的映射信息（例如，选择VLAN以表示逻辑网络）。

* 与一个或多个类型的交换机进行通信，以根据映射进行配置。这可以是在虚拟机管理程序上运行的代理的形式，或者远程登录到交换机并重新配置的代码。

另外，如果您的交换技术需要 nova-compute 以特殊方式创建 vNIC，则可能需要创建一个特殊的 vif-plugging 模块，以便与交换机一起使用。 然而，鉴于现有的插件集，很可能已经有您需要的vif插件类型。 重要的是，尽可能保持 vif 插件尽可能简单，以避免 nova 与网络细节复杂化。 例如，您不应该将 VLAN ID传递给 nova，nova 只应该创建基本设备，并且有一个 neutron 插件代理负责设置与该vlan的连接。

不需要修改任何其他nova代码，因为此代码仅使用所有插件中相同的逻辑Neutron API。

### Useful Next Steps

* 阅读管理指南中的 Neutron 概述，了解基本组件：http://docs.openstack.org/trunk/openstack-network/admin/content/ch_overview.html

* 浏览Neutron API指南，了解每个插件必须实现的API：http://docs.openstack.org/api/openstack-network/2.0/content/index.html

* 获取 Neutron 代码（http://launchpad.net/neutron）并根据管理员指南运行它。

* 查看*neutron/plugins*目录中的现有插件，以了解插件的实现

* 参见 `nova-compute vif-plugging` 的例子。在nova代码库中，请参阅 *nova/virt/libvirt/vif.py*。

### Plugin FAQ

* 问：我可以在同一时间运行多个插件吗？

答：不可以，对于给定的Neutron API，一次只能运行一个插件。 那是因为一个插件是实现一个特定的API调用的代码块。 只能运行一个插件，但并不意味着你只能与一种类型的交换机进行交互。 一个插件可以有多个驱动程序可以与不同类型的交换机交互。例如，Cisco插件与多种类型的交换机通话。 没有正式的驱动程序接口，但是我们鼓励人们以通用方式编写与交换机通话的代码，以便其他插件能够利用它。驱动程序通常是能够与特定交换机型号或系列交换机通信的代码。驱动程序通常将具有用于标准配置操作的方法，例如为端口添加一个特定的VLAN。

答： 是的，使用“meta-plugin”调用两个不同现有插件代码。https://github.com/openstack/neutron/tree/master/neutron/plugins/metaplugin

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