# OVS DB Schema

*ovs/db/schema*

## `class DbSchema(object)`

ovsdb database schema 的封装

### `def __init__(self, name, version, tables)`

```
    def __init__(self, name, version, tables):
        self.name = name
        self.version = version
        self.tables = tables

        # "isRoot" was not part of the original schema definition.  Before it
        # was added, there was no support for garbage collection.  So, for
        # backward compatibility, if the root set is empty then assume that
        # every table is in the root set.
        if self.__root_set_size() == 0:
            for table in six.itervalues(self.tables):
                table.is_root = True

        # Find the "ref_table"s referenced by "ref_table_name"s.
        #
        # Also force certain columns to be persistent, as explained in
        # __check_ref_table().  This requires 'is_root' to be known, so this
        # must follow the loop updating 'is_root' above.
        for table in six.itervalues(self.tables):
            for column in six.itervalues(table.columns):
                self.__follow_ref_table(column, column.type.key, "key")
                self.__follow_ref_table(column, column.type.value, "value")
```

* `name`：数据库名称
* `version`：数据库版本
* `tables`：以 `TableSchema` 封装的数据库中的所有表


### `def from_json(json)`

静态方法，从 json 的数据格式中解析 schema 的数据。创建一个 `DbSchema` 实例。









## `class TableSchema(object)`

数据库中表的封装




### `def from_json(json, name)`

从 json 数据中构造表的封装







## `class ColumnSchema(object)`

数据库表的列封装

```
    def __init__(self, name, mutable, persistent, type_):
        self.name = name
        self.mutable = mutable
        self.persistent = persistent
        self.type = type_
        self.unique = False
```

### `def from_json(json, name)`

从 json 数据中构造 Column






