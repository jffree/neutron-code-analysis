# 为Neutron提供新的扩展

## 简介

Neutron 具有可插拔的架构，具有多个扩展点。 本文档涉及与新型Neutron v2内核（aka monolithic）插件，ML2机制驱动程序和L3服务插件相关的方面。 本文件将首先涵盖贡献过程中的一些面向过程的方面，并提供一个如何指导，展示如何从0 LOC到成功地为Neutron提供新的扩展。 在本指南的其余部分，我们将尝试尽可能多地使用实际的例子，以便人们能够从中获得工作解决方案。

本指南适用于希望在OpenStack Networking项目中想要深入开发人员。 如果您是一名开发人员，希望在不与Neutron社区互动的情况下提供基于Neutron的解决方案，那么您可以自由地执行此操作，但是现在可以停止阅读，因为本指南不适合您。

非参考实现的插件和驱动程序称为“第三方”代码。这包括支持供应商产品的代码以及支持开源网络实现的代码。

在Kilo发布之前，这些插件和驱动程序被包含在Neutron树中。 在Kilo周期期间，第三方插件和驱动程序进行了称为分解的过程的第一阶段。 在此阶段，每个插件和驱动程序将其大部分逻辑移动到单独的git仓库，同时在DB模型和迁移（也可能是一些配置示例）中留下了一个薄的`shim`在Neutron树中。

在Liberty周期中，分解概念是通过允许第三方代码完全从树中独立开来得出的结论。已经提供了进一步的扩展机制来更好地支持改变API或数据模型的外部插件和驱动程序。

out-of-tree可以是任何公开的东西：它可能是git.openstack.org的repo，也可能是tarball，pypi包等。一个插件/驱动维护者团队自治，以促进共享 ，重用，创新和发布out-of-tree的可交付成果。 尽管核心团队的核心成员可以参与促进out-of-tree一些必须功能的开发，但核心团队成员不被建议参与这一过程。

本指南旨在将您作为与Neutron集成但存在在单独存储库中的代码维护者。

## 贡献过程

如果要使用您的技术扩展OpenStack Networking，并且您希望在OpenStack项目的可见性范围内执行此操作，请遵循以下准则和示例。 我们将介绍以下最佳做法：

* 设计与开发;
* 测试和持续集成;
* 缺陷管理;
* 为插件的特定代码提供后端管理
* DevStack集成
* 文档

一旦你有了一切，你可能希望将你的项目添加到中子子项目列表中。有关详细信息，请参阅[Adding or removing projects to the stadium](http://docs.openstack.org/developer/neutron/stadium/governance.html#adding-or-removing-projects-to-the-stadium)。

## 设计和开发

假设你有一个工作的仓库，对自己的回购的任何开发都不需要任何关于Neutron的蓝图，规格或错误。 但是，如果您的项目是Neutron Stadium 的一部分，您将被期望参与 Four Opens原则，这意味着您的设计应该在公开场合完成。 因此，鼓励您为自己的存储库中的更改提交文档。

如果您的代码托管在git.openstack.org上，则会自动提供gerrit审查系统。 贡献者应遵循与Neutron相似的审查准则。 但是，作为维护者，您可以灵活地选择谁可以批准/合并您自己的repo中的更改。

建议您设置第三方CI系统（但不是必需，请参阅[策略](http://docs.openstack.org/developer/neutron/policies/thirdparty-ci.html)）。 这将提供检查第三方代码以与Neutron 改变相违背的工具。有关更详细的建议，请参阅下面的测试和持续集成。

设计文件仍然可以以Restructured Text（RST）文件的形式提供，在同一第三方库库存中。 如果需要对普通Neutron代码进行更改，则可能需要提交RFE。不过，每一种情况都是不同的，您可以从Neutron核心审查员那里获取需要采取哪些步骤的指导。

## 测试和持续集成

以下策略仅是建议，因为第三方CI测试不是强制性要求。 然而，绝大多数插件/驱动程序的贡献者都积极参与中子开发社区，因为他们从经验中学到了自己的代码是如何落后于Neutron核心代码库的。

* 您应该在自己的外部库中运行单元测试（例如，在git.openstack.org上，Jenkins设置是免费的）。

* 您的第三方CI应通过功能测试验证与Neutron的第三方集成。第三方CI是一种沟通机制。该机制的目标如下：
 * 当有人作出了可能破坏您的代码的更改时，它会传达给您。然后由您维护受影响的插件/驱动程序，以确定故障是暂时的还是真实的，并解决问题。
 * 它与patch作者通信，他们可能会打破插件/驱动程序。如果他们与所涉及的插件/驱动程序的维护者有时间/能力/关系，那么他们可以（自行决定）工作来进行修复。
 * 它可以向社区通报，是否正在积极维护给定的插件/驱动程序。
 * A maintainer that is perceived to be responsive to failures in their third-party CI jobs is likely to generate community goodwill.

值得注意的是，如果插件/驱动程序存储库由git.openstack.org托管，由于目前的openstack-infra限制，不可能让第三方CI系统参与到这个repo的gate pipeline中。 这意味着在合并过程中向repo提供的唯一验证是通过单元测试。Post-merge 钩子仍然可以被利用来提供第三方CI反馈，并提醒您潜在的问题。 如上所述，第三方CI系统将继续验证Neutron核心提交。 这将允许他们检测何时发生不兼容的更改，无论它们在Neutron还是在第三方repo。

## 缺陷管理

影响第三方代码的错误不应在launchpad上的neutron项目中提交。错误跟踪可以在您选择的任何系统中完成，但是通过在启动板中创建第三方项目，可以使用launchpad的`also affects project`功能更容易地跟踪影响Neutron和你的代码的错误。

### 安全问题

以下是如何处理您的repo中的安全问题的一些答案，从这个[openstack-dev邮件列表消息](http://lists.openstack.org/pipermail/openstack-dev/2015-July/068617.html)中获取：

* 应如何管理您的问题的安全性？

OpenStack漏洞管理团队（VMT）遵循一个文件化流程，当需要时基本上可以被任何项目团队重用。

* OpenStack安全小组应该参与吗？

OpenStack VMT直接监督OpenStack[源代码存储库的一个子集](https://wiki.openstack.org/wiki/Security_supported_projects)的漏洞报告和披露。 不过，尽管他们不属于该项目，但仍然很乐意回答您对自己项目的漏洞管理有任何疑问。 随时在公共场合或私人接触到VMT。

此外，VMT是更大的[OpenStack Security项目团队](http://governance.openstack.org/reference/projects/security.html)的自治子组。如果您想获得他们的意见或帮助有关安全相关的问题（漏洞或其他方面），他们知识渊博并且反应迅速。

* 需要提交CVE吗？

它可以变化很大。 如果红帽这样的商业发行版本正在重新分配软件的易受攻击版本，那么即使您不要求自己也可以分配一个软件。 或者报告者可以要求一个; 报告者甚至可能会与已经指派/获得CVE的组织联系，然后才能与您联系。

* 维护者需要发布OSSN或等效文档吗？

OpenStack安全公告（OSSA）是OpenStack VMT的官方出版物，仅涵盖支持VMT的软件。 OpenStack Security Notes（OSSN）由OpenStack Security项目团队中的编辑者发布，用于更一般的安全主题，甚至可能涵盖与OpenStack一起使用的非OpenStack软件中的问题，因此可以自行决定是否将 能够适应OSSN的特定问题。

然而，这些都是相当任意的标签，事实上，真正重要的是，漏洞被认真处理，并广泛宣布，而不仅仅是在相关的OpenStack邮件列表上，而且还优选地在更广泛的地方发布如[开源安全邮件列表](http://oss-security.openwall.org/wiki/mailing-lists/oss-security)。目标是及时获取有关您的漏洞的信息，减轻使用您软件的人员的时间损耗。

* 还有什么要考虑的吗？

OpenStack VMT正在尝试重塑自身，以便在“Big Tent”的背景下更好地扩展规模。这包括确保策略/流程文档更易于消费，甚至可以在使用软件的项目团队中重新使用，这超出我们章程的范围。 这是一项正在进行的工作，欢迎任何关于如何使这个功能对每个人都有好处的投入。

## 后端管理策略

本节仅适用于在Kilo和早期版本中在Neutron树中具有代码的第三方维护者。一旦Kilo版本不再受支持，它将被淘汰。

如果对树外第三方代码进行的更改需要在稳定的分支中回传到树内部，则可以提交一个审阅，而不需要相应的主分支更改。 核心审核人员将为稳定的分支机构评估变更，以确保后端是合理的，并且不会影响Neutron核心代码的稳定性。

## DevStack集成策略

当开发和测试新的或现有的插件或驱动程序时，DevStack提供的帮助是非常有价值的：DevStack可以帮助所有的软件位安装，配置正确，更重要的是以可预测的方式。 对于DevStack集成，有几个选项可用，它们可能或可能没有意义，具体取决于您是否提供新的或现有的插件或驱动程序。

如果你提供一个新的插件，选择的方法应该基于[Extras.d Hooks的外部托管插件](http://docs.openstack.org/developer/devstack/plugins.html#extras-d-hooks)。 使用extra.d钩子，DevStack集成与第三方集成库位于同一位置，在处理基于DevStack的开发/测试部署时，可以带来最大的灵活性。

最后考虑的第三方CI设置是值得的：如果使用[Devstack Gate](https://git.openstack.org/cgit/openstack-infra/devstack-gate)，它将提供可在devstack-gate-wrap脚本运行的特定时间执行的钩子功能。 例如，[Neutron功能作业](https://git.openstack.org/cgit/openstack-infra/project-config/tree/jenkins/jobs/neutron.yaml)使用它们。 有关详细信息，请参阅[devstack-vm-gate-wrap.sh](https://git.openstack.org/cgit/openstack-infra/devstack-gate/tree/devstack-vm-gate-wrap.sh)。

## 项目初始设置

下面的操作方法假定第三方库将被托管在git.openstack.org上。 这可以让您轻松了解整个OpenStack CI基础设施，并且可以从开始为您的新的或现有的驱动程序/插件做出贡献。 以下列表是http://docs.openstack.org/infra/manual/creators.html上可以找到的总结版本。 它们是为了让你离开地面而必须完成的最低限度。

* 创建公共存储库：这可以是个人git.openstack.org repo或任何公开的git repo，例如https://github.com/john-doe/foo.git。这将是一个临时缓冲区，用于在git.openstack.org上提供一个缓冲区。

* 初始化存储库：如果重新启动，您可以选择使用cookiecutter来获取一个框架项目。 您可以在https://git.openstack.org/cgit/openstack-dev/cookiecutter上学习如何使用cookiecutter。 如果要从现有Neutron模块构建存储库，则可能现在要跳过此步骤，首先构建历史记录（下一步），然后返回到初始化存储库的剩余部分，其他文件由cookiecutter生成 （如tox.ini，setup.cfg，setup.py等）。

* 在git.openstack.org上创建一个存储库。 为此，您需要OpenStack小组的帮助。 值得注意的是，您只需在git.openstack.org上创建存储库即可。 这是您选择是否要从干净的板岩开始的时间，或者您想要导入在上一步骤中创建的repo。 在后一种情况下，可以通过在project-config / gerrit / project.yaml中指定项目的上游部分来实现。[仓库创建者指南](http://docs.openstack.org/infra/manual/creators.html)中记录了步骤。

* 要求将Launchpad用户分配给创建的核心团队。本节[介绍步骤](http://docs.openstack.org/infra/manual/creators.html#update-the-gerrit-group-members)。

* 修复，修复，修复：在这一点上，你有一个外部工作基础。 您可以针对新的git.openstack.org项目开发，与使用任何其他OpenStack项目的方法相同：您有pep8，docs和python27 CI作业，在发布到Gerrit时验证您的修补程序。 例如，您需要做的一件事是在自己的setup.cfg中为您的插件或驱动程序定义一个入口点，类似于在ODL的setup.cfg中如何完成。

* 在setup.cfg中定义插件或驱动程序的入口点

* 创建第三方CI帐户：如果您还没有，请按照第三方CI的说明进行操作。

## 国际化支持

OpenStack致力于广泛的国际支持。国际化（I18n）是使OpenStack无所不在的重要领域之一。推荐每个项目支持i18n。

本节介绍如何设置翻译支持。本节中的描述使用以下变量：

* repository : openstack/${REPOSITORY} (e.g., openstack/networking-foo)

* top level python path : ${MODULE_NAME} (e.g., networking_foo)

### oslo.i18n

每个子项目库应该有自己的oslo.i18n集成包装器模块`${MODULE_NAME}/_i18n.py`。详情见http://docs.openstack.org/developer/oslo.i18n/usage.html。

从`${MODULE_NAME}/_i18n.py`导入`_（）`。

### 设置翻译支持

您需要创建或编辑以下文件才能开始翻译支持：

* setup.cfg

* babel.cfg

我们在https://review.openstack.org/#/c/98248/上提供了一个oslo 项目的例子。

将以下内容添加到setup.cfg中：

```
[extract_messages]
keywords = _ gettext ngettext l_ lazy_gettext
mapping_file = babel.cfg
output_file = ${MODULE_NAME}/locale/${MODULE_NAME}.pot

[compile_catalog]
directory = ${MODULE_NAME}/locale
domain = ${MODULE_NAME}

[update_catalog]
domain = ${MODULE_NAME}
output_dir = ${MODULE_NAME}/locale
input_file = ${MODULE_NAME}/locale/${MODULE_NAME}.pot
```

请注意，`${MODULE_NAME}`用于所有名称。

创建babel.cfg，内容如下：

```
[python: **.py]
```

### 翻译是能

要更新和导入翻译，您需要在project-config中进行更改。 https://review.openstack.org/#/c/224222/可以找到一个很好的例子。 在这样做之后，将运行必要的工作，并将/从翻译基础设施推送消息目录。

## 与 Neutron 整合到一起

### 配置文件

中子的setup.cfg的[files]部分的data_files不包含任何第三方引用。这些位于第三方repo自己的setup.cfg文件的同一部分。

* 注意：在配置文件中命名节时应小心。 当Neutron服务或代理启动时，oslo.config从所有指定的配置文件加载部分。 这意味着如果一个部分[foo]存在于多个配置文件中，则重复的设置将会相冲突。 因此，建议使用第三方字符串，例如， [vendor_foo]。

从Mitaka版本开始，配置文件不在git存储库中维护，而应生成如下：

```
tox -e genconfig
```

如果“tox”环境不可用，则可以运行以下脚本来生成配置文件：

```
./tools/generate_config_file_samples.sh
```

建议子项目不要将他们的配置文件保存在各自的树中，而是使用与Neutron相似的方法生成它们。

### 数据库模型和迁移

第三方repo可能包含自己的表的数据库模型。 尽管这些表位于Neutron数据库中，但它们完全由第三方代码独立管理。 第三方代码不得以任何方式修改Neutron核心表。

每个repo都有其自己的扩张和合同[ alembic migration branches](https://docs.openstack.org/developer/neutron/devref/alembic_migrations.html#migration-branches)。第三方repo的alembic migration branches只能在repo所有的表格上运作。

* 注意：添加新表时应小心。为了防止表名的冲突，需要使用供应商/插件字符串对它们进行前缀。

* 注意：第三方维护者可能会选择为其表使用单独的数据库。这可能会使DBMS中不支持这种情况的模式有外键限制的情况复杂化。建议第三方维修人员。

第三方repo所拥有的数据库表可以引用中子核心表中的字段。然而，插件/驱动程序repo的alembic分支将永远不会更新它不拥有的表的任何部分。

**注意：当引用的项目更改时会发生什么？**

问：如果驱动表有一个Neutron核心表的参考（例如一个外键），并且引用的项目在Neutron里改变了，你该怎么办？

答：幸运的是，这应该是极少的事情。 Neutron核心审核人员不会允许这样的改变，除非有非常仔细思考的设计决定。 该设计将包括如何解决受影响的任何第三方代码。 （这是您应该继续积极参与Neutron开发者社区的另一个好原因。）

用于Neutron的`neutron-db-manage`数据包装器脚本检测安装的第三方资料库的异常分支，升级命令自动适用于所有这些。 第三方repo必须在安装时注册其异常迁移。 这通过在setup.cfg中提供entrypoint来完成，如下所示：

对于名为networking-foo的第三方repo，请将alembic_migrations目录作为entrypoint添加到neutron.db.alembic_migrations组中：

```
[entry_points]
neutron.db.alembic_migrations =
    networking-foo = networking_foo.db.migration:alembic_migrations
```

### 数据库模型/迁移测试

这是一个[模板功能测试](http://docs.openstack.org/developer/neutron/devref/template_model_sync_test.html)第三方维护者可以用来开发他们的repo中的模型与迁移同步的测试。建议每个第三方CI设置这样的测试，并定期对Neutron主机运行。

### Entry Points

[Python setuptools ](https://pythonhosted.org/setuptools)在一个环境的全局命名空间中安装软件包的所有入口点。因此，每个第三方回购可以在其自己的setup.cfg文件中定义其包的自己的[entry_points]。

例如，对于network-foo repo：

```
[entry_points]
console_scripts =
    neutron-foo-agent = networking_foo.cmd.eventlet.agents.foo:main
neutron.core_plugins =
    foo_monolithic = networking_foo.plugins.monolithic.plugin:FooPluginV2
neutron.service_plugins =
    foo_l3 = networking_foo.services.l3_router.l3_foo:FooL3ServicePlugin
neutron.ml2.type_drivers =
    foo_type = networking_foo.plugins.ml2.drivers.foo:FooType
neutron.ml2.mechanism_drivers =
    foo_ml2 = networking_foo.plugins.ml2.drivers.foo:FooDriver
neutron.ml2.extension_drivers =
    foo_ext = networking_foo.plugins.ml2.drivers.foo:FooExtensionDriver
```

注意：建议将foo包含在这些入口点的名称中，以避免与可能在相同环境中安装的其他第三方软件包发生冲突。

### API扩展

扩展可以通过两种方式加载：

* 使用`append_api_extensions_path()`库API。该方法在中子树中的`neutron/api/extensions.py`中定义。

* 在部署时利用`api_extensions_path`配置变量。请参阅中子树中的示例配置文件`etc/neutron.conf`，该变量被注释。

### 服务提供者

如果您的项目以与VPNAAS和LBAAS相同的方式使用服务提供商，则可以在`project_name.conf`文件中指定服务提供商：

```
[service_providers]
# Must be in form:
# service_provider=<service_type>:<name>:<driver>[:default][,...]
```

为了使Neutron正确加载，请确保在代码中执行以下操作：

```
from neutron.db import servicetype_db
service_type_manager = servicetype_db.ServiceTypeManager.get_instance()
service_type_manager.add_provider_configuration(
    YOUR_SERVICE_TYPE,
    pconf.ProviderConfiguration(YOUR_SERVICE_MODULE))
```

当您实例化您的服务插件类时通常需要这样做。

### 驱动接口

用于参考实现的接口（VIF）驱动程序在`neutron/agent/linux/interface.py`中定义。第三方接口驱动程序应在自己的repo内的相似位置进行定义。

接口驱动程序的入口点是Neutron配置选项。在[default]部分中由安装人员配置此项。例如：

```
[default]
interface_driver = networking_foo.agent.linux.interface.FooInterfaceDriver
```

### Rootwrap Filters

如果第三方repo需要用于Neutron内核不使用的命令的rootwrap filter，则过滤器应在第三方repo中定义。

例如，要在repo networking-foo中添加用于命令的rootwrap filter：

* 在repo中，创建文件：`etc/neutron/rootwrap.d/foo.filters`

* 在repo的setup.cfg中将过滤器添加到data_files中：

```
[files]
data_files =
    etc/neutron/rootwrap.d =
        etc/neutron/rootwrap.d/foo.filters
```

### Extending python-neutronclient

第三方组件的维护者可能希望向Neutron CLI客户端添加扩展。感谢https://review.openstack.org/148318现在可以完成。请参阅客户端命令扩展。

### Other repo-split items

(These are still TBD.)

* Splitting policy.json? ToDo Armando will investigate.

* Generic instructions (or a template) for installing an out-of-tree plugin or driver for Neutron. Possibly something for the networking guide, and/or a template that plugin/driver maintainers can modify and include with their package.

