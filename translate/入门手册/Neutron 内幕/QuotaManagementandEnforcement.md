# Quota Management and Enforcement

Neutron API暴露的大部分资源都受到配额限制。 Neutron API公布了管理这种配额的扩展。在将请求发送到插件之前，API层执行配额限制。

配额限制的默认值在neutron.conf中指定。 管理员用户可以根据每个项目覆盖这些默认值。 限制存储在 Neutron 数据库中; 如果给定的资源和项目没有找到限制，则使用此类资源的默认值。每个项目获得配置文件中指定的配额限制，Liberty版本已经不再使用基于配置的配额管理。

请注意，Neutron不支持每个用户的配额限制和层次化多租户的配额管理（事实上Neutron根本不支持分层多租户）。 此外，在AMQP总线上监听的RPC接口上，目前还没有实施配额限制。

Plugin 和 ML2 驱动程序不应该对他们管理的资源执行配额。然而，subnet_allocation [1](https://docs.openstack.org/developer/neutron/devref/quota.html#id7) 扩展是一个例外，下面将讨论。

这里讨论的配额管理和执行机制适用于已经在配额引擎中注册的每个资源，不管这种资源是否属于核心Neutron API或其扩展之一。

## 高层视图

Neutron 配额制度有两个主要组成部分：

* The Quota API extension;

* The Quota Engine.

这两个组件都依赖于配额驱动程序。中子代码库中目前定义了两个配额驱动程序：

* neutron.db.quota.driver.DbQuotaDriver

* neutron.quota.ConfDriver

不过后一种驱动程序已被弃用。

配额API扩展会处理配额管理，而配额引擎组件则会处理配额执行。此API扩展名与任何其他扩展名一样加载。因此，插件必须通过在 `supported_extension_aliases` 属性中包含 `quotas` 来显式支持它。

在配额API中，简单的CRUD操作用于管理项目配额。请注意，删除项目配额时的当前行为是将该项目的配额限制重置为配置默认值。API扩展不会使用身份服务验证项目标识符。

配额执行是配额引擎的责任。在向插件发送请求之前，RESTful API控制器尝试从配额引擎获取客户端请求中指定的资源的预留。如果保留成功，则继续将该操作发送到插件。

要保留成功，请求的资源总额加上预留的资源总额加上已经存储在数据库中的资源总量不应超过项目的配额限额。

最后，配额管理和执行依赖于“配额驱动程序”[2](https://docs.openstack.org/developer/neutron/devref/quota.html#id8)，其任务基本上是执行数据库操作。

## 配额管理

配额管理组件相当简单。

然而，与绝大多数Neutron扩展不同，它使用它自己的控制器类[3](https://docs.openstack.org/developer/neutron/devref/quota.html#id9)。 此类不执行POST操作。 列表，获取，更新和删除操作由通常的索引，显示，更新和删除方法实现。 这些方法只需调用配额驱动程序即可获取项目配额或更新它们。

_update_attributes方法在控制器生命周期中只调用一次。 该方法动态更新Neutron的资源属性映射[4](https://docs.openstack.org/developer/neutron/devref/quota.html#id10)，以便为配额引擎管理的每个资源添加一个属性。 在此控制器中执行请求授权，只允许“admin”用户修改项目的配额。 由于不使用 neutron 策略引擎，因此无法配置哪些用户可以使用policy.json来管理配额。

处理配额管理的驱动业务是：

* `delete_tenant_quota`，它只是从给定项目标识符的“配额”表中删除所有条目;
* `update_quota_limit` 在给定项目标识符和给定资源名称的“配额”项目中添加或更新条目;
* `_get_quotas`，它为一组资源和给定的项目标识符获得限制
* `_get_all_quotas`，其行为类似于_get_quotas，但对于所有项目。

## 资源使用信息

Neutron 有两种跟踪资源使用信息的方法：

* `CountableResource`，其中通过计算资源表中的行和该资源的预留来强制执行配额限制时计算资源使用情况。
* `TrackedResource`，依赖于特定的表跟踪使用数据，并且只有当该表中的数据与实际使用和预留的资源不同步时才执行显式计数。

`CountableResource` 和 `TrackedResource` 之间的另一个区别是前者调用一个插件方法来计算资源。 因此，`CountableResource` 应该用于不作用于Neutron数据库的插件。 Neutron配额引擎将使用的实际类由配额配置部分中的 `track_quota_usage` 变量决定。 如果为True，将创建`TrackedResource` 实例，否则配额引擎将使用 `CountableResource` 实例。 资源创建由`neutron.quota.resource` 模块中的 `create_resource_instance` 工厂方法执行。

从性能角度来看，使用表格跟踪资源使用具有一些优势，尽管不是根本。 实际上，执行查询以明确计数对象所需的时间将随着表中记录的数量而增加。 另一方面，使用TrackedResource将获取单个记录，但是具有在操作完成后必须执行UPDATE语句的缺点。 然而，CountableResource实例不仅仅是在资源的相关表上执行SELECT查询，而是调用一个插件方法，该方法可能会执行几个语句，有时甚至在返回之前与后端进行交互。 与本章另一部分讨论的资源预留概念相结合时，资源使用跟踪对于运营正确性也将变得重要。

跟踪配额使用并不像每次创建或删除资源时更新计数器一样简单。 事实上，可以通过几种方法创建 Neutron 能力限制的资源。 尽管RESTful API请求是最常见的，但可以通过在AMQP总线上列出的RPC处理程序创建资源，例如创建DHCP端口或通过插件操作（如创建路由器端口的插件）。

为此，`TrackedResource` 实例被初始化为对跟踪使用数据的资源的模型类的引用。 在对象初始化期间，为此类安装了SqlAlchemy事件处理程序。 事件处理程序在插入或删除记录之后执行。 作为该资源的结果使用数据，一旦操作完成，将被标记为“脏”，以便下次使用数据被请求时，它将同步数据库中的资源使用计数。 即使这个解决方案有一些缺点，列在“例外和注意事项”部分，它比以下解决方案更可靠：

* 每次操作完成时，使用新的“正确”值更新使用计数器。

* 定期任务将配额使用数据与中子数据库中的实际数据进行同步。

最后，无论是否使用CountableResource或TrackedResource，配额引擎总是调用其count（）方法来检索资源使用。 因此，从配额引擎的角度来看，CountableResource和TrackedResource绝对没有区别。

## 配额执行

在向插件发出请求之前，Neutron'base'控制器[5](https://docs.openstack.org/developer/neutron/devref/quota.html#id11)尝试对所请求的资源进行预留。 通过调用neutron.quota.QuotaEngine中的make_reservation方法进行预约。 进行预约的过程是相当简单的：

* 获取当前资源的用法。 这通过在每个请求的资源上调用计数方法，然后检索预留资源的数量来实现。
* 通过调用_get_tenant_quotas方法来获取所请求资源的当前配额限制。
* 获取所选资源的过期预留。 这一数额将从资源使用中减去。 由于在大多数情况下不会有任何过期的保留，所以这种方法实际上需要较少的DB操作，而不是为每个请求执行一个未过期的保留资源。
* 对于每个资源计算其余量，并且验证所请求的资源量是否小于净空。
* 如果上述所有资源都为真，则保留保存在数据库中，否则会引发OverQuotaLimit异常。

配额引擎能够预留多种资源。 然而，值得注意的是，由于目前的neutron API层的结构，不存在对多个资源进行预留的实际情况。 为此，避免对每个资源重复查询的性能优化不是当前实现的一部分。

为了确保正确的操作，在创建预留的事务中获取row-level锁。读取使用数据时获取锁定。如果写入认证失败，这可能发生在主动/主动集群（如MySQL galera）中，装饰器neutron.db.api.retry_db_errors将在DBDeadLock异常引发时重试该事务。虽然非锁定方法是可能的，但是已经发现，由于非锁定算法增加了碰撞的机会，所以处理DBDeadlock的成本仍然低于在检测到冲突时重试操作的成本。对这个方向进行了一项针对知识产权分配业务的研究，但同样的原则也适用于此[6](https://docs.openstack.org/developer/neutron/devref/quota.html#id12)。然而，为了数据库级别的锁定，移动将是今后配额实施的必要条件。

提交和取消预订就像删除预订一样简单。当提交保留时，所提交的资源现在存储在数据库中，因此预留本身应该被删除。中止配额引擎在取消预约时简单地删除记录（即：请求未能完成），并在保留提交时也将配额使用信息标记为脏（即：请求完全正确）。通过在neutron.quota.QuotaEngine中分别调用commit_reservation和cancel_reservation方法来提交或取消预留。

预订不是多年生的。永久保留将最终耗尽项目的配额，因为当一名API工作人员在一个操作过程中崩溃时永远不会被删除。预留到期目前设置为120秒，并且不可配置，至少尚未。计算资源使用量时，不计入到期预留。在创建预订时，如果发现任何过期的预留，则该项目和资源的所有过期预留将从数据库中删除，从而避免过期的预留的建立。

## 为插件设定资源跟踪

默认情况下，插件不能利用资源跟踪。 让插件明确声明应该跟踪哪些资源是精确的设计选择，旨在尽可能地限制在现有插件中引入错误的机会。

因此，插件必须声明它要跟踪哪个资源。 这可以使用neutron.quota.resource_registry模块中可用的tracked_resources装饰器来实现。 理想情况下，装饰器应用于插件的__init__方法。

装饰器在输入中接受关键字参数的列表。 参数的名称必须是资源名称，参数的值必须是DB模型类。 例如：

```
@resource_registry.tracked_resources(network=models_v2.Network,
port=models_v2.Port, subnet=models_v2.Subnet, subnetpool=models_v2.SubnetPool)
```

将确保跟踪网络，端口，子网和子网资源。 在理论上，可以多次使用这个装饰器，而不是仅仅使用__init__方法。 然而，这将最终导致代码可读性和可维护性问题，因此开发人员强烈建议将此装饰程序专用于插件的__init__方法（或插件在初始化期间仅调用一次的任何其他方法）。

## RPC接口和RESTful控制器的实现者注意事项

不幸的是，Neutron没有一个层，在调度从插件的操作之前被调用，这可以通过AMQP API从RESTful和RPC中被利用。 特别是RPC处理程序直接调用插件，而不需要任何请求授权或配额执行。

因此，RPC处理程序必须明确指出是否要调用插件来创建或删除任何类型的资源。 这是通过在RPC处理程序执行终止后确保修改后的资源被标记为脏的方式实现的。 为了这个目的，开发人员可以使用module_resources_dirty装饰器在模块neutron.quota.resource_registry中提供。

装饰器将扫描注册资源的整个列表，并将其使用情况跟踪器的脏状态存储在数据库中，以便在插件操作期间创建或销毁项目的资源。

## 例外和注意事项

请注意配额执行引擎的以下限制：

* 从子网池（特别是共享池）neutron 配子网也需要配额限制检查。但是，这种检查不是由配额引擎执行的，而是通过在neutron.ipam.subnetalloc模块中实现的机制。这是因为配额引擎不能满足子网分配配额的要求。

* 配额引擎还提供了一个limit_check例程，强制配额检查而不创建预留。这种执行配额的方式是非常不可靠的，并被保留机制所取代。它没有被删除，以确保树木插件和扩展，杠杆不被破坏。

* SqlAlchemy事件可能不是检测资源使用情况变化的最可靠方法。由于事件机制监视数据模型类，对于正确的配额执行来说，始终使用对象关系映射创建和删除资源是至关重要的。例如，使用query.delete调用删除资源不会触发事件。 SQLAlchemy事件应该被认为是采用中间件缺少持久API对象的临时措施。
由于CountableResource实例不跟踪使用数据，所以在进行预约时，不会获取写意图锁。因此，具有CountableResource的配额引擎不是并发安全的。

* 用于指定哪些资源使能跟踪的机制依赖于在注册限额资源之前插入插件的事实。因此，当启用跟踪时，无法验证资源是否实际存在。开发人员应特别注意确保资源名称的正确指定。

* 代码假设使用情况跟踪器是值得信赖的真实来源：如果他们报告使用计数器，并且脏位未设置，该计数器是正确的。如果它的肮脏，肯定是计数器不同步。这不是非常强大的，因为在切换use_tracked_resources配置变量时重新启动时可能会出现问题，因为过期的计数器可能被信任进行预约。而且，如果服务器在API操作完成之后但在提交预留之前崩溃，则会发生相同的情况，因为实际的资源使用情况发生了变化，但相应的使用情况跟踪器没有被标记为脏。

## References
[1]	Subnet allocation extension: http://git.openstack.org/cgit/openstack/neutron/tree/neutron/extensions/subnetallocation.py
[2]	DB Quota driver class: http://git.openstack.org/cgit/openstack/neutron/tree/neutron/db/quota_db.py#n33
[3]	Quota API extension controller: http://git.openstack.org/cgit/openstack/neutron/tree/neutron/extensions/quotasv2.py#n40
[4]	Neutron resource attribute map: http://git.openstack.org/cgit/openstack/neutron/tree/neutron/api/v2/attributes.py#n639
[5]	Base controller class: http://git.openstack.org/cgit/openstack/neutron/tree/neutron/api/v2/base.py#n50
[6]	http://lists.openstack.org/pipermail/openstack-dev/2015-February/057534.html