# Neutron L3 Agent 之 FipRulePriorityAllocator

*neutron/l3/fip_rule_priority_allocator.py*

## `class FipPriority(object)`

```
class FipPriority(object):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return str(self.index)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, FipPriority):
            return (self.index == other.index)
        else:
            return False
```

## `class ItemAllocator(object)`

*neutron/agent/l3/item_allocator.py*

```
    def __init__(self, state_file, ItemClass, item_pool, delimiter=','):
        """Read the file with previous allocations recorded.

        See the note in the allocate method for more detail.
        """
        self.ItemClass = ItemClass
        self.state_file = state_file

        self.allocations = {}

        self.remembered = {}
        self.pool = item_pool

        read_error = False
        for line in self._read():
            try:
                key, saved_value = line.strip().split(delimiter)
                self.remembered[key] = self.ItemClass(saved_value)
            except ValueError:
                read_error = True
                LOG.warning(_LW("Invalid line in %(file)s, "
                                "ignoring: %(line)s"),
                            {'file': state_file, 'line': line})

        self.pool.difference_update(self.remembered.values())
        if read_error:
            LOG.debug("Re-writing file %s due to read error", state_file)
            self._write_allocations()
```

* 参数说明：
 1. `state_file` 用于保存分配出去的数据的文件路径
 2. `ItemClass` 用于表示数据的类
 3. `item_pool` 数据的资源池
 4. `delimiter` 分割符 

1. 调用 `_read` 方法读取数据记录文件中的已经存在的数据，并将这些数据保存在 `remembered` 变量中
2. 清除资源池 pool 中的，在 `remembered` 中的数据记录（因为这些数据已经分配，不可以再次分配）。
3. 若读取数据存储文件发生了异常，则调用 `_write_allocations` 重新创建数据记录文件，并将已分配的数据写入其中

### `def _read(self)`

读取数据记录文件中的已经存在的数据

### `def _write_allocations(self)`

1. 确定要写入数据文件的数据
2. 调用 `_write` 实现数据写入

### `def _write(self, lines)`

```
    def _write(self, lines):
        with open(self.state_file, "w") as f:
            f.writelines(lines)
```

### `def release(self, key)`

回收某一个分配出去的数据

### `def allocate(self, key)`

分配一个数据

## `class FipRulePriorityAllocator(ItemAllocator)`


```
class FipRulePriorityAllocator(ItemAllocator):
    """Manages allocation of floating ips rule priorities.
        IP rule priorities assigned to DVR floating IPs need
        to be preserved over L3 agent restarts.
        This class provides an allocator which saves the priorities
        to a datastore which will survive L3 agent restarts.
    """
    def __init__(self, data_store_path, priority_rule_start,
                 priority_rule_end):
        """Create the necessary pool and create the item allocator
            using ',' as the delimiter and FipRulePriorityAllocator as the
            class type
        """
        pool = set(FipPriority(str(s)) for s in range(priority_rule_start,
                                                      priority_rule_end))

        super(FipRulePriorityAllocator, self).__init__(data_store_path,
                                                       FipPriority,
                                                       pool)
```

1. 创建一个资源池
2. 调用 `ItemAllocator` 的初始化方法
3. `data_store_path`：`/opt/stack/data/neutron/fip-priorities` 用来存储分配出去的数据

```
[root@node1 ~]# cat /opt/stack/data/neutron/fip-priorities 
172.16.100.245,57483
```