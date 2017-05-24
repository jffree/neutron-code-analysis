# oslo_db

## 安装

```
$ pip install oslo.db
```

* 安装 SQL 后端

```
$ pip install psycopg2
```

```
$ pip install PyMySQL
```

```
$ pip install pysqlite
```

### 使用 PostgreSQL

如果您使用PostgreSQL，请确保为您的发行版安装PostgreSQL客户端开发包。在Ubuntu上完成如下：

```
$ sudo apt-get install libpq-dev
$ pip install psycopg2
```

如果没有首先安装libpq-dev，则psycopg2的安装将失败。请注意，即使在虚拟环境中，libpq-dev也在系统环境中安装。

### 使用 MySQL-python 

在 OpenStack中，PyMySQL 是 oslo.db 的默认 MySQL DB API 驱动程序。 但是您仍然可以使用 MySQL-python 作为替代DB API的驱动程序。 对于 MySQL-python，您必须为您的发行版安装MySQL客户端开发包。 在Ubuntu上完成如下：

```
$ sudo apt-get install libmysqlclient-dev
$ pip install MySQL-python
```

如果未安装 libmysqlclient-dev，MySQL-python 的安装将失败。请注意，即使在虚拟环境中，MySQL软件包也将在系统中安装。

## [配置选项](https://docs.openstack.org/developer/oslo.db/opts.html)

oslo.db使用oslo.config来定义和管理配置选项，以允许部署者控制应用程序如何使用底层数据库。

## 如何使用

### 回话处理

会话处理使用 `oslo_db.sqlalchemy.enginefacade` 系统实现。该模块提供了一个函数装饰器以及一个上下文管理器方法来将 `Session` 和 `Connection` 对象传递给一个函数或块。

两种调用形式都需要使用上下文对象。该对象可以是任何类，尽管与装饰器形式一起使用时，需要特殊的检测。

**上下文管理器形式如下：**

```
from oslo_db.sqlalchemy import enginefacade


class MyContext(object):
    "User-defined context class."


def some_reader_api_function(context):
    with enginefacade.reader.using(context) as session:
        return session.query(SomeClass).all()


def some_writer_api_function(context, x, y):
    with enginefacade.writer.using(context) as session:
        session.add(SomeClass(x, y))


def run_some_database_calls():
    context = MyContext()

    results = some_reader_api_function(context)
    some_writer_api_function(context, 5, 10)
```

**装饰器形式**直接从用户定义的上下文访问属性。上下文必须使用 `oslo_db.sqlalchemy.enginefacade.transaction_context_provider()` 装饰器进行装饰。每个函数都必须接收上下文参数：

```
from oslo_db.sqlalchemy import enginefacade

@enginefacade.transaction_context_provider
class MyContext(object):
    "User-defined context class."

@enginefacade.reader
def some_reader_api_function(context):
    return context.session.query(SomeClass).all()


@enginefacade.writer
def some_writer_api_function(context, x, y):
    context.session.add(SomeClass(x, y))


def run_some_database_calls():
    context = MyContext()

    results = some_reader_api_function(context)
    some_writer_api_function(context, 5, 10)
```

当不需要 `Session` 对象时，可以使用 `connection` 修饰符，例如当 SQLAlchemy Core 是首选：

```
@enginefacade.reader.connection
def _refresh_from_db(context, cache):
    sel = sa.select([table.c.id, table.c.name])
    res = context.connection.execute(sel).fetchall()
    cache.id_cache = {r[1]: r[0] for r in res}
    cache.str_cache = {r[0]: r[1] for r in res}
```

**注意：** `context.session` 和 `context.connection` 属性必须在适当的 `writer/reader` 块（装饰器或contextmanager方法）的范围内访问。否则会引发 `AttributeError`。

装饰器形式也可以与隐式接收第一个位置参数的类和实例方法一起使用：

```
class DatabaseAccessLayer(object):

    @classmethod
    @enginefacade.reader
    def some_reader_api_function(cls, context):
        return context.session.query(SomeClass).all()

    @enginefacade.writer
    def some_writer_api_function(self, context, x, y):
        context.session.add(SomeClass(x, y))
```

**注意：** `enginefacade` 装饰器必须在 `classmethod` 之前应用，否则在导入时将会得到一个 `TypeError` （因为 `enginefacade` 将尝试在描述符上使用 `inspect.getargspec()`，而不是绑定方法，请参考 Data Model 部分 Python语言参考的详细信息）。

两种方法的交易和连接的范围是透明的。 连接的配置来自标准的 `oslo_config.cfg.CONF` 集合。 在使用数据库开始之前，可以使用 `oslo_db.sqlalchemy.enginefacade.configure()` 函数为引擎引擎设置其他配置：

```
from oslo_db.sqlalchemy import enginefacade

enginefacade.configure(
    sqlite_fk=True,
    max_retries=5,
    mysql_sql_mode='ANSI'
)
```

### 模型使用的基类

```
from oslo_db.sqlalchemy import models


class ProjectSomething(models.TimestampMixin,
                       models.ModelBase):
    id = Column(Integer, primary_key=True)
    ...
```

### DB API后端支持

```
from oslo_config import cfg
from oslo_db import api as db_api


_BACKEND_MAPPING = {'sqlalchemy': 'project.db.sqlalchemy.api'}

IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING)

def get_engine():
    return IMPL.get_engine()

def get_session():
    return IMPL.get_session()

# DB-API method
def do_something(somethind_id):
    return IMPL.do_something(somethind_id)
```

### 数据库迁移扩展

oslo_db.migration的可用扩展

# 参考

[SQLAlchemy ORM教程之一：Create](http://www.jianshu.com/p/0d234e14b5d3)

[SQLAlchemy ORM教程之二：Query](http://www.jianshu.com/p/8d085e2f2657)

[ SQLAlchemy技术文档（中文版）（上） ](http://www.cnblogs.com/iwangzc/p/4112078.html)

[ SQLAlchemy技术文档（中文版）（中） ](http://www.cnblogs.com/iwangzc/p/4114913.html)