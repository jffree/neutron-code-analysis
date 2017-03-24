# 高效的Neutron：100种具体方法来提高您对 Neutron 的贡献

这里有一些技巧可以早就一个伟大的 Neutron 开发人员：写好代码，有效地审查，听取同伴反馈等。本文档的目的是通过实例来描述我们在项目中遇到的陷阱以及好的和坏的实践经验， 这些都有可能减慢或加快我们对 Neutron 的贡献。

通过阅读和一同贡献这样的知识库，您的开发和审查周期将变得更短，因为您将学习（并教会您以后的其他人）注意什么，以及如何积极主动，以防止负面反馈，极小的编程错误，编写更好的测试等等...简而言之，如何成为一个高效的 Neutron 开发人员。

下面的注释意味着自由形式和简短的设计。 它们并不意味着替换或复制[OpenStack文档](http://docs.openstack.org/)，或任何类似于[peer-review notes](http://docs.openstack.org/infra/manual/developers.html#peer-review)或者[team guide](http://docs.openstack.org/project-team-guide/)项目文档。 因此，如果这个捷径有助于扩展浓缩信息，那么参考文献应应该受到青睐。 如果有意义的话，我们会尝试把这些笔记整理一下。你认为合适的情况下，你可以 随意添加，调整，删除它。 请这样做，考虑到你和其他Neutron开发者是读者。 在开发和审查过程中积累您的经验，并添加那些您认为会使您和其他开发者更容易的任何建议。

## 开发更好的软件

### 插件开发

记录常见的陷阱以及在插件开发过程中的好的经验。

* 使用mixin类作为最后的手段。他们可以成为增加行为的强大工具，但其功能也是一个弱点，因为他们可能会向[MRO](https://www.python.org/download/releases/2.3/mro/)引入[不可预知的行为](https://review.openstack.org/#/c/121290/)等问题。

* 替代mixins，如果您需要添加与ML2相关的行为，请考虑使用[扩展管理器](http://specs.openstack.org/openstack/neutron-specs/specs/juno/neutron-ml2-mechanismdriver-extensions.html)。

* 如果您对数据库类方法进行更改，例如可以继承的调用方法，请考虑可能具有控制器[后端](https://review.openstack.org/#/c/116924/)插件的影响。

* 如果您更改ML2插件或ML2插件使用的组件，请考虑可能对其他插件的[影响](http://lists.openstack.org/pipermail/openstack-dev/2015-October/076134.html)。

* 想L2和L3数据库基类添加功能时，不要假定另一端存在与服务器交互的消息代理。插件可能根本不依赖[代理](https://review.openstack.org/#/c/174020/)。

* 开发插件扩展时，请注意所需的功能。 [扩展描述](https://github.com/openstack/neutron/blob/b14c06b5/neutron/api/extensions.py#L122)可以指定您正在开发的扩展所需的功能列表。 通过声明此列表，如果不满足要求，则服务器将无法启动，从而避免导致系统在运行时遇到不确定的行为。

### 数据库交互



