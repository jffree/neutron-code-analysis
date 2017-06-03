# oslo_db.sqlalchemy.enginefacade

## `class _symbol`

代表了一个独一无二的符号

## `class _Default(object)`

标志一个默认值

### `def resolve(cls, value)`

类方法，获取一个用 `_Default` 封装的真实值

### `def resolve_w_conf(cls, value, conf_namespace, key)`

类方法，从 `conf_namespace` 中获取 `key` 的键值。没有的话则从 `value` 中获取。

### `def is_set(cls, value)`

判断一个 `value` 是否被设置了一个默认值。

### `def is_set_w_conf(cls, value, conf_namespace, key)`

判断一个 `value` 是否被设置了一个默认值，或者在 `conf_namespace` 中被设置。

## `class _TransactionContextManager(object)`

回话上下文的管理器，主要是对 `_TransactionFactory` 的封装。

### `def __init__`

初始化方法，默认情况下实现一个 `_TransactionFactory` 的实例。

```
        if root is None:
            self._root = self
            self._root_factory = _TransactionFactory()
        else:
            self._root = root
```

### `def _factory(self)`

属性方法

```
    @property
    def _factory(self):
        """The :class:`._TransactionFactory` associated with this context."""
        return self._root._root_factory
```

### `def get_legacy_facade(self)`

### `def get_engine(self)`

### `def get_sessionmaker(self)`

### `def dispose_pool(self)`

### `def make_new_manager(self)`

从当前的管理器克隆一个新的管理器

### `def patch_factory(self, factory_or_manager)`

替代当前管理器中的 `_TransactionFactory` 实例

### `def patch_engine(self, engine)`

替代当前管理器中 `_TransactionFactory` 中的 `engine`。

### `def _clone(self, **kw)`

在新配置的基础上克隆出一个新的管理器

### `def replace(self)`

### `def writer(self)`

### `def reader(self)`

### `def allow_async(self)`

## `class _TransactionFactory(object)`

### `__init__`

初始化一些使用数据库（SQLAlchemy）模块的配置选项

### `def configure_defaults(self, **kw)`

```
self._configure(True, kw)
```

### `def configure(self, **kw)`

```
self._configure(False, kw)
```

### `def _configure(self, as_defaults, kw)`

更新配置选项

### `def get_legacy_facade(self)`

构造一个 `LegacyEngineFacade` 实例。

### `def _start(self, conf=False, connection=None, slave_connection=None)`

本方法只会执行一次。

构造 `SQLAlchemy` 所需要的 URL配置，引擎配置和会话配置。

在此基础上构造 `_writer_engine`、`_writer_maker`、`_reader_engine`、`_reader_maker`

### `def _setup_for_connection(self, sql_connection, engine_kwargs, maker_kwargs):`

被 `_start` 方法调用，创建连接数据库的 engine 和 session

### `def _create_connection(self, mode)`

返回数据库的一个 Connection 对象

### `def _create_session(self, mode, bind=None)`

创建一个 Session 对象

### `def _create_factory_copy(self)`

复制当前的工厂实例

### `def _args_for_conf(self, default_cfg, conf)`

读取 conf，若配置中没有相关选项，则使用 `default_cfg` 中的选项。

### `def dispose_pool(self)`

销毁 engine 连接池中的空闲连接

## `class LegacyEngineFacade(object)`

用于从oslo.db中删除全局引擎实例的辅助类。

这个类也是对 `_TransactionFactory`，若是 `_TransactionFactory` 发生改动，也不会影响前后的兼容性。









