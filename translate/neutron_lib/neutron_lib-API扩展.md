# API Extensions

API扩展提供了引入新API功能的标准化方法。尽管 neutron-lib 项目本身并不服务于API，但是 neutron 项目确实并利用了来自 neutron-lib 的API扩展框架。

API扩展包含以下高级结构：

* 指定扩展程序的静态元数据的API定义。此元数据包括有关扩展的基本详细信息，例如其名称，描述，别名等，以及其扩展资源/子资源以及必选/可选扩展。 这些定义存在于 `neutron_lib.api.definitions` 包中。

* API参考记录了扩展程序添加/修改的 APIs/resources。本文档采用 rst 格式，用于生成[openstack API参考](https://developer.openstack.org/api-ref/networking/v2/)。 API参考文献生活在 neutron-lib 项目仓库的 *api-ref/source/v2* 目录下。

* 扩展描述符类，必须在扩展目录中定义，用于支持扩展的 neutron 或其他子项目。 这个具体类将扩展的元数据提供给API服务器。 这些扩展类位于 neutron-lib 之外，但是使用来自 `neutron_lib.api.extensions` 的基类。 有关更多详细信息，请参阅下面有关使用 neutron-lib 扩展类的部分。

* API扩展插件实现本身。这是实现扩展行为的代码，应该执行扩展定义的操作。 此代码位于其各自的项目存储库中，而不在 neutron-lib 中。 有关详细信息，请参阅 [neutron api extension dev-ref](https://github.com/openstack/neutron/blob/master/doc/source/devref/api_extensions.rst)。

## 使用 neutron_lib 的基本扩展类

`neutron_lib.api.extensions` 模块提供了消费者可以用来定义扩展描述符的一组基本扩展描述符类。 对于那些在 `neutron_lib.api.definitions` 中具有API定义的扩展，可以使用 `APIExtensionDescriptor` 类。 例如：

```
from neutron_lib.api.definitions import provider_net
from neutron_lib.api import extensions


class Providernet(extensions.APIExtensionDescriptor):
    api_definition = provider_net
    # nothing else needed if default behavior is acceptable
```

对于尚未在 `neutron_lib.api.definitions` 中定义的扩展，它们可以继续使用 `ExtensionDescriptor`，就像历史上一样。