# SQLAlchemy 理解

## 架构

![架构](http://images2015.cnblogs.com/blog/720333/201610/720333-20161019162806842-1144462684.png)

## engine

用于与数据库建立连接

```
from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://root:123@127.0.0.1:3306/t1", max_overflow=5)
```

## Mapper

将一个类与一个表建立映射关系。

```
my_table = Table("my_table", metadata,
                 Column('id', Integer, primary_key=True),
                 Column('type', String(50)),
                 Column("some_alt", Integer)
                )

class MyClass(object):
    pass

mapper(MyClass, my_table,
       polymorphic_on=my_table.c.type,
       properties={
                   'alt':my_table.c.some_alt
      })
```

## Table

代表着数据库中的一张表。

若使用相同的表名和相同的 `MetaData` 实例来构造 `Table` 实例，则会返回一个相同的 `Table` 实例。

```
mytable = Table("mytable", metadata,
                Column('mytable_id', Integer, primary_key=True),
                Column('value', String(50))
          )
```

## Metadata

用于存储一些列表的集合以及他们的关联模式。

绑定 `engine` 的 `Metadata` 的实例，那么实例里面的 `Table` 可以用来执行 SQL 操作。

## Session

用来管理对 ORM 对象的持续性操作。

```
Session = sessionmaker(autoflush=False)
sess = Session()
```

## Connection

维护这与数据库的链接。

## event

注册事件通知，在数据库发生相应的事件时，会调用注册的方法

## 其他

`__mapper_args__`  传递给 ORM 中 Mapper 的配置选项

`__table_args__` 传递给 ORM 中 Table 的配置选项

`__tablename__`  表的名称

`_sa_instance_state` 保存 ORM 对象的状态

# 参考

[SQLAlchemy 对象缓存和刷新](http://www.cnblogs.com/fengyc/p/5369301.html?utm_source=tuicool&utm_medium=referral)

[on delete cascade](http://www.cnblogs.com/xgcblog/archive/2011/08/25/2152918.html)

[web.py开发web 第四章 Sqlalchemy（事件监听与初始化）](https://my.oschina.net/zhengnazhi/blog/120800)

[How to close sqlalchemy connection in MySQL](https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql)

[sqlalchemy中使用event设置条件触发短信与邮件通知](http://www.cnblogs.com/yasmi/p/5056089.html)