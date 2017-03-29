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



