# Neutron Ovs Command

## `class Command(object)`

*neutron/agent/ovsdb/native/api.py*

抽象基类。

定义了一个抽象方法 `execute`，用来立即执行该命令。

## `class BaseCommand(api.Command)`

*neutron/agent/ovsdb/native/command.py*

```
class BaseCommand(api.Command):
    def __init__(self, api):
        self.api = api
        self.result = None
```

### `def execute(self, check_error=False, log_errors=True)`

利用 transaction 的 `__enter__` 和 `__exit__` 方法，来完成命令的执行

## `class AddManagerCommand(BaseCommand)`

增加 manager 命令，通过 `txn.insert` 实现插入新记录，同时增加 `Open_vSwitch` 的 `manager_options` 记录。

相当于执行 ` ovs-vsctl set-manager`

## `class GetManagerCommand(BaseCommand)`

获取 Manager 命令，直接读取 `api._tables` 的记录。

相当于执行 `ovs-vsctl get-manager`

## `class RemoveManagerCommand(BaseCommand)`

1. 验证该 manager 是否存在
2. 在 `Open_vSwitch` 的 `manager_options` 记录中删除该 manager
3. 删除 `Manager` 表中的该项记录

相当于执行 `ovs-vsctl del-manager`

## `class AddBridgeCommand(BaseCommand)`

`may_exist`：代表该记录可能存在，需要先进行检查

1. 创建新的 `Bridge` 表的记录
2. 增加 `Open_vSwitch` 中的 `bridges` 的记录
3. 增加 `Port` 表的记录
4. 增加 `Interface` 表的记录

相当于执行 `ovs-vsctl add-br`

## `class DelBridgeCommand(BaseCommand)`

1. 删除与该 bridge 相关的所有 port 的记录
2. 删除 `Bridge` 中该记录
3. 删除 `Open_vSwitch` 中该 `bridges` 的记录

相当于执行 `ovs-vsctl del-br`

## `class BridgeExistsCommand(BaseCommand)`

直接检查 `Bridge` 表中是否存在该 bridge 的记录
 
相当于执行 `ovs-vsctl br-exists br-tun`

## `class PortToBridgeCommand(BaseCommand)`

判断该 port 属于哪个 bridge

相当于执行：`ovs-vsctl port-to-br int-br-ex`

## `class InterfaceToBridgeCommand(BaseCommand)`

判断该 interface 属于哪个 bridge

相当于执行命令：`ovs-vsctl iface-to-br patch-int`

## `class ListBridgesCommand(BaseCommand)`

列出所有 bridger 的名称。

相当于执行 `ovs-vsctl list-br` 的命令

## `class BrGetExternalIdCommand(BaseCommand)`

相当于执行 `ovs-vsctl br-get-external-id`

## `class BrGetExternalIdCommand(BaseCommand)`

相当于执行 `ovs-vsctl br-set-external-id` 命令

## `class DbCreateCommand(BaseCommand)`

创建一个表的记录

相当于执行 `ovs-vsctl create `

## `class DbDestroyCommand(BaseCommand)`

相当于执行 `ovs-vsctl destroy `

## `class DbSetCommand(BaseCommand)`

相当于执行  `ovs-vsctl set `

## `class DbClearCommand(BaseCommand)`

相当于执行 `ovs-vsctl clear`

## `class DbGetCommand(BaseCommand)`

相当于执行 `ovs-vsctl get`

## `class DbListCommand(BaseCommand)`

相当于执行 `ovs-vsctl list `

## `class DbFindCommand(BaseCommand)`

相当于执行 `ovs-vsctl find` 

## `class SetControllerCommand(BaseCommand)`

相当于执行 `ovs-vsctl set-controller `

## `class DelControllerCommand(BaseCommand)`

相当于执行 `ovs-vsctl del-controller`

## `class GetControllerCommand(BaseCommand)`

相当于执行 `ovs-vsctl get-controller `

## `class SetFailModeCommand(BaseCommand)`

相当于执行 `ovs-vsctl set-fail-mode`

## `class AddPortCommand(BaseCommand)`

相当于执行 `ovs-vsctl add-port `

## `class DelPortCommand(BaseCommand)`

相当于执行 `ovs-vsctl del-port`

## `class ListPortsCommand(BaseCommand)`

相当于执行 `ovs-vsctl list-ports`

## `class ListIfacesCommand(BaseCommand)`

相当于执行 `ovs-vsctl list-ifaces `