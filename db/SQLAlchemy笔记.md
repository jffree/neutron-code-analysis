# SQLAlchemy 学习笔记（一）

## ORM 类的构造

[Declare a Mapping](http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping)

### python descriptor

[python中基于descriptor的一些概念（下）](http://www.cnblogs.com/btchenguang/archive/2012/09/18/2690802.html)

[sqlalchemy 中的 descriptor](http://docs.sqlalchemy.org/en/latest/glossary.html#term-descriptors)

### mapping

[Classical Mappings](http://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html#classical-mapping)

## `declared_attr`

Declarative treats attributes specifically marked with @declared_attr as returning a construct that is specific to mapping or declarative table configuration.

[`class sqlalchemy.ext.declarative.declared_attr(fget, cascading=False)`](http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html?highlight=declarative%20declared_attr#sqlalchemy.ext.declarative.declared_attr)

# 参考

[SQLAlchemy 1.2 Documentation](http://docs.sqlalchemy.org/en/latest/index.html)

