# ML2扩展管理器

ML2的扩展管理器在Juno推出（更多的细节可以在批准的 [spec](http://specs.openstack.org/openstack/neutron-specs/specs/juno/neutron-ml2-mechanismdriver-extensions.html) 中找到）。这些功能允许扩展ML2资源，而实际上不必向ML2引入横切问题。 该机制已经应用于多个用例，目前使用此框架的扩展可在 [ml2/extensions](https://github.com/openstack/neutron/tree/master/neutron/plugins/ml2/extensions) 下使用。

# 调用 ML2 Plugin

当为  extension，service plugin 或Neutron的任何其他部分编写代码时，您必须调用核心插件方法，以便mutate state while you have a transaction open on the session that you pass into the core plugin method。

ML2中的端口，网络和子网的创建和更新方法都具有 precommit 阶段和 postcommit  阶段。在 precommit 阶段，数据预计将完全持续到数据库，ML2驱动程序将利用这一时间将信息 relay 到 neutron 以外的后端。在 transaction 中调用ML2插件会违反这个语义，因为数据不会被持久化到数据库中; 这个操作将会失败并且导致整个 transaction 被回滚，后端将与 neutron 数据库中的状态不一致。

为了防止这种情况，这些方法受到装饰器的保护，如果在活动 transaction 中使用具有会话的上下文来调用`RuntimeError`，那么它将引发 `RuntimeError`。 装饰器可以在`neutron.common.utils.transaction_guard`上找到，可以在Neutron的其他地方使用，以保护希望在 transaction 之外被调用的功能。








