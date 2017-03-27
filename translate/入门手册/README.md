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

记录常见的陷阱以及在数据库开发过程中的良好做法。

* [first\(\)](http://docs.sqlalchemy.org/en/rel_1_0/orm/query.html#sqlalchemy.orm.query.Query.first) 不引发异常。

* 不要使用[delete\(\)](http://docs.sqlalchemy.org/en/rel_1_0/orm/query.html#sqlalchemy.orm.query.Query.delete)来删除对象。 删除查询不会加载该对象，因此不会触发可以执行诸如重新计算配额或更新父对象的修订版本的操作`sqlalchemy`事件。 有关使用批量删除操作可能出现的所有问题的更多详细信息，请参阅上述链接中的“**警告**”部分。

* 对于PostgreSQL，如果您使用GROUP BY SELECT列表中的所有内容必须是聚合SUM（...），COUNT（...）等，或在GROUP BY中使用。

不正确的方法如下：

```
q = query(Object.id, Object.name,
          func.count(Object.number)).group_by(Object.name)
```

正确的方法：

```
q = query(Object.id, Object.name,
          func.count(Object.number)).group_by(Object.id, Object.name)
```

* 请注意[InvalidRequestError](http://docs.sqlalchemy.org/en/latest/faq/sessions.html#this-session-s-transaction-has-been-rolled-back-due-to-a-previous-exception-during-flush-or-similar)异常。 甚至有一个[Neutron bug](https://bugs.launchpad.net/neutron/+bug/1409774)注册了它。 请记住，嵌套事务块时也可能会发生此错误，而最内部的块在没有正确回调的情况下引发错误。 考虑[savepoints](http://docs.sqlalchemy.org/en/rel_1_0/orm/session_transaction.html#using-savepoint)是否适合您的用例。

* 在设计相互关联的数据模型时，请注意如何建模关系的加载[策略](http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#using-loader-strategies-lazy-loading-eager-loading)。 例如，连接关系可以比其他连接关系非常有效（可参考[路由器网关](https://review.openstack.org/#/c/88665/)或[网络可用性区域](https://review.openstack.org/#/c/257086/)）。

* 如果添加与Neutron对象的关系，Neutron对象在被检索时其关系对象在大多数情况下将被引用，请确保使用lazy ='joined'参数进行关系，以便相关对象作为同一查询的一部分加载 。 否则，默认方法是“select”，它会发出一个新的DB查询，以检索每个相关对象，从而对性能产生不利影响。 例如，见[patch 88665](https://review.openstack.org/#/c/88665/)，这导致了显着的改进，因为路由器检索功能总是包括网关接口。

* 相反，如果关系仅在角落中使用，则不要使用lazy ='joined'，因为在关系包含很多对象的情况下，JOIN语句的成本可能会很大。 例如，参见[patch 168214](https://review.openstack.org/#/c/168214/)，它通过避免加入IP分配表来将子网检索减少〜90％。

* 当对现有对象（例如网络）进行扩展时，请确保以无需额外的数据库查找即可计算对象上的数据的方式编写它们。 如果不可能，请确保在一个 list 操作期间批量执行数据库查找。 否则，1000个对象的 list 调用将从一个常量很少的DB查询变为1000个DB查询。 例如，见[patch 257086](https://review.openstack.org/#/c/257086/)，它将可用区域代码从不正确的样式更改为数据库友好的。

* 有时在代码中我们使用以下结构：

```
def create():
   with context.session.begin(subtransactions=True):
       create_something()
       try:
           _do_other_thing_with_created_object()
       except Exception:
           with excutils.save_and_reraise_exception():
               delete_something()

def _do_other_thing_with_created_object():
   with context.session.begin(subtransactions=True):
       ....
```

问题是当`_do_other_thing_with_created_object`中引发异常时，它被捕获在except块中，但该对象不能被删除，因为`_do_other_thing_with_created_object`的内部事务已经被 rolled back。 为避免这种嵌套事务应该被使用。 对于这种情况，帮助函数`safe_creation`已在*neutron/ db/_utils.py*中创建。 所以上面的例子应该替换为：

```
_safe_creation(context, create_something, delete_something,
               _do_other_thing_with_created_object)
```

`_do_other_thing_with_created_object`函数中使用了嵌套事务。

`_safe_creation`函数也可以传递`transaction = False`参数，以防止创建任何事务，只是为了利用异常逻辑上的自动删除。

* 请注意`ResultProxy.inserted_primary_key`，它返回最后插入的主键列表，而不是最后插入的主键：

```
result = session.execute(mymodel.insert().values(**values))
# result.inserted_primary_key is a list even if we inserted a unique row!
```

* 请注意pymysql，它可以用一个元素静默地打开一个列表（隐藏`ResultProxy.inserted_primary_key`的错误使用，例如）：

```
e.execute("create table if not exists foo (bar integer)")
e.execute(foo.insert().values(bar=1))
e.execute(foo.insert().values(bar=[2]))
```

* 第二个插入应该崩溃（提供的是列表，期望的是整数）。至少在mysql和postgresql做后端时会崩溃，但是使用pymysql会成果，因为它将它们转换为：

```
INSERT INTO foo (bar) VALUES (1)
INSERT INTO foo (bar) VALUES ((2))
```

## 系统开发

记录在调用系统命令和与linux utils交互时所遇到的陷阱是良好做法。

* 当一个 patch 需要现有工具中的新平台工具或新功能时，请检查常见的平台是否带有上述功能。 此外，使用`UpgradeImpact`标记这样的补丁以提高其可见性（以便这些补丁可在团队会议期间引起核心团队的注意）。 更多细节在[审查指南](http://docs.openstack.org/developer/neutron/policies/code-reviews.html#neutron-spec-review-practices)。

## Eventlet并发模型

记录在使用eventlet和猴子补丁时所遇到的陷阱是良好做法。

* 不要在不使用`lockutils`信号量保护操作的情况下对SQL使用`with_lockmode（'update'）`查询。 对于操作者可能选择的一些SQLAlchemy数据库驱动程序（例如MySQLdb），可能会产生一个具有数据库锁的协程时产生临时死锁。 以下wiki提供了更多的细节：
[https://wiki.openstack.org/wiki/OpenStack_and_SQLAlchemy#MySQLdb_.2B_eventlet_.3D_sad](https://wiki.openstack.org/wiki/OpenStack_and_SQLAlchemy#MySQLdb_.2B_eventlet_.3D_sad)

## Mocking and testing

在编写测试时记录常见陷阱是良好做法。对于更详细的内容，请访问测试部分。

* 优选低级测试与全路径测试（例如，不通过客户端调用测试数据库）。前者在单元测试中是有利的，而后者在功能测试中是有利的。

* 使用具体的断言（assert（not）InAssert（Not）IsInstance，Assert（Not）IsNone等）而非通用的断言（assertTrue / False，assertEqual），因为它们引发更有意义的错误：

```
def test_specific(self):
    self.assertIn(3, [1, 2])
    # raise meaningful error: "MismatchError: 3 not in [1, 2]"

def test_generic(self):
    self.assertTrue(3 in [1, 2])
    # raise meaningless error: "AssertionError: False is not true"
```

* 使用模式`self.assertEqual(expected, observed)`不是相反的，它有助于审查者了解哪一个是non-trivial断言中的预期/观察值。 当断言失败时，预期值和观测值也会在输出中标注。

* 使用具体断言`assertions (assertTrue, assertFalse)`而非（`assertTrue，assertFalse`）。

* 不要编写不测试预期代码的测试。这可能看起来很愚蠢，但很容易就可以做到很多mock。在您的代码更改之前，确保您的测试符合预期。

* 避免大量使用mock库来测试代码。 如果你的代码需要一个以上的mock来确保它是正确的，它需要被重构成更小，可测试的单位。 否则我们依赖于*fullstack/tempest/api*测试来测试所有的真实行为，我们最终得到包含太多隐藏依赖关系和副作用的代码。

* 所有修改错误的行为都应该包括一个防止回归的测试。如果你做了一个改变，没有打破测试，这意味着代码没有被充分的测试，没有借口不去进行测试。

* 测试失败案例。使用mock副作用来抛出必要的异常来测试你的`except`子句。

* 不要模拟现有的违反这些准则的测试。我们试图将所有这些更多的测试替换为更多的测试，创造更多的工作。如果您需要帮助撰写测试，请联系IRC的测试中尉和团队。

* `Mocking open()`是一个危险的做法，因为它可能导致意外的错误，如错误[1503847](https://bugs.launchpad.net/neutron/+bug/1503847).实际上，当内置的open方法在测试期间被mocked时，一些实用程序（如债务收集器）可能仍然依赖于真实的东西，可能 最终使用mock，而不是真正寻找的东西。 如果你必须使用，请考虑`OpenFixture`，但最好不要使用 `mock open()`。

### 向后兼容

在扩展RPC接口时所记录常见陷阱是良好做法。

* 熟悉[升级版审核指南】（https://docs.openstack.org/developer/neutron/devref/upgrade.html#upgrade-review-guidelines）。

#### 弃用

有时我们想以非向后兼容的方式重构事物。在大多数情况下，您可以使用[debtcollector](http://docs.openstack.org/developer/debtcollector)来标记弃用。配置项具有[oslo.config支持的弃用选项](http://docs.openstack.org/developer/oslo.config/opts.html)。

弃用过程必须遵循标准的弃用要求。在Neutron发展方面，这意味着：

* 一个launchpad bug来跟踪弃用。

* 标记不推荐使用的项目的patch。如果弃用影响用户（配置项，API更改），则必须包含[发行说明](http://docs.openstack.org/developer/reno/usage.html)。

* 等待至少一个周期和至少三个月的线性时间。

* 一个补丁，用于删除不推荐使用的项目。请确保在此补丁的提交消息中引用原始的launchpad bug。

### 可扩展性问题

编写需要处理大量数据的代码时记录常见陷阱是良好做法。

### 翻译及日志

在编写代码时记录常见陷阱良好做法。

* 让自己熟悉[OpenStack日志记录指南](http://specs.openstack.org/openstack/openstack-specs/specs/log-guidelines.html#definition-of-log-levels)，以避免在不合适的级别记录跟踪日志。

* logger只能通过unicode值。例如，不要直接传递异常或其他对象（LOG.error（exc），LOG.error（port）等））。详见：[http://docs.openstack.org/developer/oslo.log/usage.html#no-more-implicit-conversion-to-unicode-str](http://docs.openstack.org/developer/oslo.log/usage.html#no-more-implicit-conversion-to-unicode-str)

* 不要将异常传递到LOG.exception中：它已被Python日志记录模块隐含地包含在日志消息中。

* 当前线程上下文中没有注册异常时，请勿使用LOG.exception：**3.5之前的Python 3.x版本已知会失败**。

### 项目接口

编写用于与其他项目（如Keystone或Nova）进行交互的代码时记录常见陷阱良好做法。

### 文档化你的代码

## 快速 Landing patches

### 适当地调整patch

* 除非绝对必要，否则不要在一个补丁中进行多个更改。 清理作用于事物的附近的功能或修复一个小的bug，你注意到这些使得补丁很难审查。 它也使cherry-picking和恢复非常困难。 即使显而易见的微小变化，例如重新格式化您的变更之外的空白可能会对审核人员造成负担，并导致合并冲突。

* 如果修复或功能需要代码重构，请将重构提交为与更改逻辑的修补程序不同的patch。 否则，审阅者难以说明重构中的错误与修复/功能所需的更改之间的差异。 如果这是一个错误修复，尝试在重构之前实施修复程序，以避免难以选择稳定的分支。

* 考虑您的审查的时间，然后再提交您的补丁。 需要许多小时或数天才能审核的修补程序将位于“待办事项”列表中，直到有人有多小时或几天的免费（这可能永远不会发生）。如果您的patch小但易于理解和可测试的部分提供补丁，那么您将更有可能吸引审查人员。

