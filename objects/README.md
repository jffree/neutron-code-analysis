# 关于 verioned object 是我看的比较累的一个子项目，文档太少，所以我在 readme 里面会注释写到一些总的概念。


1. versioned object 的作用是将数据库的一条记录转化为一个 object。所以，请按照数据库的观念去理解 object。
2. 如同数据库中有一对一、一对多、多对多的关系一样，object 也会存在这些关系。
3. 在 Neutron 中，*neutron/objects/base.py* 中的 `NeutronDbObject` 为实现所有 object 的基类，这个是我们的入口类。
4. 要读懂这个子项目，请从一个具体的实例入手，比如说：*neutron/objects/subnet.py* 中的 `class Subnet`。
5. 既然是对应数据库，那么肯定会有对应的增查改删的操作，这些操作在 object 中为下列的方法：
 1. 查询（获取数据库记录）：单一查询 `get_object`、批量查询 `get_objects`。
 2. 创建：`create`
 3. 修改（更新）：`update`
 4. 删除：`delete`
6. object 本身不仅可以代表数据库，每个 object 还可以转化成为 primitive 格式的数据（也就是字典类型的），primitive 类型的数据包含了 object 的所有 Field。（`obj_to_primitive`）
7. 当然，也可以从 primitive 数据转换成为一个 object。（`obj_from_primitive`）
