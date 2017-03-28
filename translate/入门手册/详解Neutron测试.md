# 建立 Neutron 的开发环境

本页介绍如何设置可用于在Ubuntu，Fedora或Mac OS X上开发Neutron的Python开发环境。这些说明假定您已经熟悉Git和Gerrit，Git和Gerrit是代码存储库镜像和代码审查工具集 但是，如果您不是，请参阅此Git教程，介绍[如何使用Git](http://git-scm.com/book/en/Getting-Started)和[本指南](http://docs.openstack.org/infra/manual/developers.html#development-workflow)介绍如何使用Gerrit和Git对OpenStack项目的代码贡献。

按照这些说明将允许您运行Neutron的单元测试。 如果您想要在完整的OpenStack环境中运行Neutron，可以使用优秀的DevStack项目来实现。 有一个wiki页面，描述[使用DevStack设置Neutron](https://wiki.openstack.org/wiki/NeutronDevstack)。

## 获取代码

```
git clone git://git.openstack.org/openstack/neutron.git
cd neutron
```

# 测试 Neutron

## 你应该关心什么

有两种方法来测试：

1. 编写单元测试是因为它们需要将补丁合并。这通常包含模拟重测试，断言您的代码像写的一样工作。

2. 尽可能多地考虑您的测试策略，如同您对其余代码一样。 适当使用不同层次的测试来提供高质量的覆盖。 你接触一个agent吗？ 根据实际系统测试！ 你在添加一个新的API吗？ 根据真实的数据库测试竞争条件！ 您是否添加了一个新的cross-cutting功能？ 测试它在真正的云上运行时到底做了什么。

您是否需要手动验证您的更改？如果是这样，接下来的几个部分将试图指导您完成Neutron的不同测试基础架构，以帮助您做出明智的决策，并最好地利用Neutron的测试产品。

## 定义

我们将讨论三类测试：单元，功能和集成。每个类别通常都针对较大的代码范围。除了广泛的分类之外，这里还有一些特点：

* 单元测试 - 应该能够在笔记本电脑上运行，直接跟踪项目的“git clone”。底层系统不能被突变，mock可以用来实现这一点。单元测试通常以功能或类为目标。

* 功能测试 - 针对预配置的环境运行（tools/configure_for_func_testing.sh）。通常测试一个组件，不使用mock代理。

* 集成测试 - 针对运行的云进行，通常针对API级别，而且还针对“场景”或“用户故事”。您可以在*tests/tempest/api*，*tests/tempest/scenario*，*test/fullstack*以及Tempest和Rally项目中找到这样的测试。

Neuron树中的测试通常由所使用的测试基础组织，而不是测试范围。 例如，'unit'目录下的许多测试调用一个API调用，并声明收到了预期的输出。 这种测试的范围是整个Neutron服务器堆栈，并且显然不是典型的单元测试中的特定的功能。

### 测试框架

单元测试（neutron/tests/unit）意图覆盖尽可能多的代码。 它们旨在测试中子树的各种部分，以确保任何新的更改不会破坏现有功能。 单元测试没有要求，也不会对其运行的系统进行更改。 他们使用内存中的sqlite数据库来测试数据库交互。

在每次测试运行开始时：

* RPC listeners are mocked away.
* 假的 Oslo 消息驱动被使用.

在每次测试运行结束时：

* mocks 自动恢复。

* 内存中的数据库被清除内容，但其模式会被维护。

* 全局的Oslo配置对象被重置。

单元测试框架可用于有效测试数据库交互，例如，分布式路由器为运行OVS代理的每个主机分配一个MAC地址。 DVR的DB混合器之一实现了一种列出所有主机MAC地址的方法。 它的测试如下所示：

```
def test_get_dvr_mac_address_list(self):
    self._create_dvr_mac_entry('host_1', 'mac_1')
    self._create_dvr_mac_entry('host_2', 'mac_2')
    mac_list = self.mixin.get_dvr_mac_address_list(self.ctx)
    self.assertEqual(2, len(mac_list))
```

它插入两个新的主机MAC地址，调用被测方法并断言其输出。测试有很多事情要做：

* 它正确地针对被测方法，而不是比所需的更大的范围。

* 它不使用mocks来声明方法被调用，它只是调用该方法并声明其输出（在这种情况下，list方法返回两个记录）。

这是允许的，该方法是建立可测试的 - 该方法具有清晰的输入和输出，没有副作用。

您可以通过将`OS_TEST_DBAPI_ADMIN_CONNECTION`设置为基于文件的URL来获取oslo.db来生成基于文件的sqlite数据库，如本邮件列表中所述。 该文件将被创建，但（混淆）不会是用于数据库的实际文件。 要查找实际文件，请在测试方法中设置一个断点，并检查`self.engine.url`。

```
$ OS_TEST_DBAPI_ADMIN_CONNECTION=sqlite:///sqlite.db .tox/py27/bin/python -m \
    testtools.run neutron.tests.unit...
...
(Pdb) self.engine.url
sqlite:////tmp/iwbgvhbshp.db
```

现在，您可以使用sqlite3检查此文件。

```
$ sqlite3 /tmp/iwbgvhbshp.db
```

### 功能测试

功能测试（neutron/tests/functional/)）旨在验证实际的系统交互。 Mocks 应该谨慎使用，如果有的话。 应该注意确保现有的系统资源不被修改，并且在测试成功和失败的情况下，在测试中创建的资源都得到了适当的清理。 请注意，当在gate运行时，功能测试从源代码编译OVS。 检查*neutron/tests/contrib/gate_hook.sh*。 其他工作目前从软件包中使用OVS。

我们来看看功能测试框架的好处。 Neutron提供了一个名为'ip_lib'的库，其中包含'ip'二进制文件。 其中一种方法称为“device_exists”，它接受设备名称和命名空间，如果设备存在于给定的命名空间中，则返回True。 很容易构建一个直接针对该方法的测试，而这样的测试将被视为“单元”测试。 然而，这样的测试应该使用什么框架呢？ 使用单元测试框架的测试不能在系统上改变状态，因此实际上无法创建设备并声明它现在存在。 这样的测试大致如下：

* 它会mock'执行'，一种执行shell命令的方法来返回一个名为'foo'的IP设备。

* 那么它会assert当'device_exists'且名称为'foo'时，它会返回True，若是其他设备名称则返回False。

* 这很可能会断言'execute'被使用如下命令：`ip link show foo`。

这样的测试的价值是有争议的。记住，新的测试不是免费的，它们需要维护。代码经常被重构，重新实现和优化。

* 还有其他方法可以确定设备是否存在（比如通过查看*/sys/class/net*），在这种情况下，测试将不得不更新。

* 使用他们的名字mock方法。当方法重命名，移动或移除时，必须更新它们的mock。由于可以避免的原因，这样会减缓开发。

* 最重要的是，测试不会断言该方法的行为。它只是断言代码是否如写的那样工作。

当为'device_exists'添加功能测试时，添加了几个框架级方法。 这些方法现在也可以被其他测试使用。 一种这样的方法在命名空间中创建一个虚拟设备，并确保在测试运行结束时清除命名空间和设备，无论使用“addCleanup”方法是成功还是失败。 该测试生成临时设备的详细信息，断言该名称的设备不存在，创建该设备，断言它现在存在，删除它，并断言它不再存在。 如果使用单元测试框架编写，这样的测试可以避免上述所有上述三个问题。

功能测试也用于瞄准较大的范围，如代理。 存在许多很好的例子：请参见OVS，L3和DHCP代理功能测试。 这样的测试针对顶级代理方法，并断言应该执行的系统交互确实被执行。 例如，要测试接受网络属性并配置该网络的dnsmasq的DHCP代理的顶级方法，则测试：

* 实例化一个DHCP代理类的实例（但不启动它的进程）。

* 使用准备的数据调用其顶级功能。

* 创建一个临时命名空间和设备，并从该命名空间调用'dhclient'。

* 声明设备成功获取了预期的IP地址。

### 全栈测试

#### 为什么？

“fullstack”测试背后的想法是填补单元+功能测试和Tempest之间的差距。 Tempest 测试运行成本高昂，并专门针对黑盒API测试。 Tempest需要运行OpenStack部署，这可能难以配置和设置。 根据测试所需的拓扑结构，完全堆栈测试通过照顾部署本身来解决这些问题。 开发人员进一步受益于全栈测试，因为它可以充分模拟真实的环境，并提供快速重现的方式来验证代码，同时还在编写它。

#### 如何做？

全栈测试建立自己的Neutron进程（服务器和代理）。在运行开始之前，他们假设工作的Rabbit和MySQL服务器。有关如何在VM上运行fullstack测试的说明，请参见下面的说明。

每个测试定义了自己的拓扑（什么和多少服务器和代理应该运行）。

由于测试运行在机器本身，全栈测试可以进行“白盒”测试。这意味着您可以通过API创建路由器，然后声明为其创建了命名空间。

全栈测试仅在Neutron资源中运行。 您可以使用Neutron API（中子服务器设置为NOAUTH，以使Keystone不在picture中）。 虚拟机可以使用类似容器的类来模拟：`neutron.tests.fullstack.resources.machine.FakeFullstackMachine`。 其使用示例可以在以下位置找到：`neutron/tests/fullstack/test_connectivity.py`。

全栈测试可以通过启动代理多次来模拟多节点测试。 具体来说，每个节点都有自己的*OVS/inuxBridge/DHCP/L3*代理副本，全部配置有相同的“主机”值。 每个OVS代理连接到它自己的一对*br-int/br-ex*，然后这些桥互连。 对于LinuxBridge代理，每个代理都在自己的命名空间中启动，名为`host- <some_random_value>`。 这些命名空间与OVS `central` 桥连接。

