# Neutron dhcp driver

在配置文件 */etc/neutron/dhcp_agent.ini* 中，我们看到默认的 dhcp agent driver 为：`dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq`

## `class Dnsmasq(DhcpLocalProcess)`

### `def check_version(cls)`

空方法

### `def existing_dhcp_networks(cls, conf)`

1. 调用 `get_confs_dir` 获取配置中 dhcp agent server 的配置文件的目录（这个目录下是一堆子目录，这些子目录都是以 network id 来命名的）
2. 读取下面的所有子目录名称（即所有使用该 dhcp agent 的网络 id）

### `def get_isolated_subnets(cls, network)`

获取 network 中孤立的 subnet（即该 subnet 没有连接到 router 上）。

### `def should_enable_metadata(cls, conf, network)`

判断是否应该为改 network 建立一个 metadata proxy

* network 可以建立 metadata proxy 条件可以使下面的任何一个：
 1. `force_metadata` 为 True，且包含 ipv4 版本、允许 dhcp 的 subnet
 2. `enable_metadata_network` 为 True、`enable_isolated_metadata` 为 True，且包含 `169.254.169.254/16` 的子网
 3. `enable_isolated_metadata` 为 True，且包含 ipv4 版本、允许 dhcp 的 isolated subnet











## `class DhcpLocalProcess(DhcpBase)`

### `def __init__(self, conf, network, process_monitor, version=None, plugin=None)`

```
    def __init__(self, conf, network, process_monitor, version=None,
                 plugin=None):
        super(DhcpLocalProcess, self).__init__(conf, network, process_monitor,
                                               version, plugin)
        self.confs_dir = self.get_confs_dir(conf)
        self.network_conf_dir = os.path.join(self.confs_dir, network.id)
        common_utils.ensure_dir(self.network_conf_dir)
```

看到了什么：**_init_ 方法会在 dhcp agent server 的配置目录下创建新的子目录，并且这些子目录都是以 network id 来命名的。**

### `def get_confs_dir(conf)`

根据配置信息中的 dhcp server 配置文件所在的目录（在 */etc/neutron/dhcp_agent.ini* 中：`dhcp_confs = $state_path/dhcp`）并将其转化为据对路径。

```
    @staticmethod
    def get_confs_dir(conf):
        return os.path.abspath(os.path.normpath(conf.dhcp_confs))
```

### `def get_conf_file_name(self, kind)`

```
    def get_conf_file_name(self, kind):
        """Returns the file name for a given kind of config file."""
        return os.path.join(self.network_conf_dir, kind)
```

### `def _remove_config_files(self)`

```
    def _remove_config_files(self):
        shutil.rmtree(self.network_conf_dir, ignore_errors=True)
```

删除数据目录下的所有文件

### `def _enable_dhcp(self)`

检查当前的网络中是否有子网允许 dhcp，若有一个则返回 True

### `def _get_process_manager(self, cmd_callback=None)`

创建一个 `ProcessManager` 的实例

### `def active(self)`

属性方法。

```
    @property
    def active(self):
        return self._get_process_manager().active
```

通过 `ProcessManager.active` 方法判断该子进程是否运行。

### `def interface_name(self)`

属性读方法

```
    @property
    def interface_name(self):
        return self._get_value_from_conf_file('interface')
```

### `def interface_name(self, value)`

属性写方法

```
    @interface_name.setter
    def interface_name(self, value):
        interface_file_path = self.get_conf_file_name('interface')
        common_utils.replace_file(interface_file_path, value)
```

### `def disable(self, retain_port=False)`

1. 删除对负责该网络调度的子进程的监测
2. 调用 `_get_process_manager` 获取该子进程的包装实例后，杀死该子进程
3. 调用 `_destroy_namespace_and_port` 删除 dhcp 的接口以及命名空间
4. 调用 `_remove_config_files` 删除与该网络相关的数据文件

### `def _destroy_namespace_and_port(self)`

1. 调用 `DeviceManager.destroy` 删除该 dhcp 使用的该网络的 port
2. 调用 `IPWrapper` 删除与该网络相关的命名空间

### `def _get_process_manager(self, cmd_callback=None)`

构造一个子进程的包装实例

### `def enable(self)`











## `class DhcpBase(object)`

抽象基类，定义了 dhcp agent driver 的框架

### `def __init__(self, conf, network, process_monitor, version=None, plugin=None)`

```
    def __init__(self, conf, network, process_monitor,
                 version=None, plugin=None):
        self.conf = conf
        self.network = network
        self.process_monitor = process_monitor
        self.device_manager = DeviceManager(self.conf, plugin)
        self.version = version
```















## `class DeviceManager(object)`

### `def __init__(self, conf, plugin)`

```
    def __init__(self, conf, plugin):
        self.conf = conf
        self.plugin = plugin
        self.driver = agent_common_utils.load_interface_driver(conf)
```

调用 `agent_common_utils.load_interface_driver` 加载实际的 interface driver。dhcp agent interface dirver 在 *dhcp_agent.ini* 中定义：`interface_driver = openvswitch`。

### `def setup(self, network)`

1. 调用 `setup_dhcp_port`

### `def setup_dhcp_port(self, network)`

1. 调用 `get_device_id` 获取一个独一无二的 device id
2. 获取该网络下允许 dhcp 服务的 subnet
3. 对于一个网络来说，dhcp port 有三种情况：第一是已经存在了（`_setup_existing_dhcp_port`）；第二是被用户手动创建的（`_setup_reserved_dhcp_port`）；第三是还未创建（`_setup_new_dhcp_port`）。本方法会依次处理这三种情况。
4. 首先调用 `_setup_existing_dhcp_port`

### `def get_device_id(self, network)`

调用 `common_utils.get_dhcp_agent_device_id` 创建一个 device id（在 network、host 一定的情况下，device id 也是一定的）

### `def _setup_existing_dhcp_port(self, network, device_id, dhcp_subnets)`

1. 查找当前网络下的 port 是否有 device_id 与该网络的 dhcp port 的 device id 一致的 port
2. 若是有该 port 则：
 1. 获取与该 Port 绑定的 ip，并判断这些 ip 是否属于 `dhcp_subnets` 。
 2. 若是有的 ip 部署于改 dhcp 所掌控的子网，则需要重新对该 Port 进行 ip 分配（保留之前在子网范围内的，去除不在子网范围内的，并且新增的子网也要在改 port 上分配ip）。调用 `plugin.update_dhcp_port` 实现。这里的 `plugin` 为 dhcp agent 的 RPC Client （`DhcpPluginApi`）。

### `def destroy(self, network, device_name)`

1. 调用 `unplug` 方法删除名为 device_name 的设备
2. 通过 RPC 调用 Server 端的 `release_dhcp_port` 方法删除该 port 在 neutron-server 数据库中的记录
 
### `def unplug(self, device_name, network)`

调用 dhcp interface driver 的 `unplug` 方法实现

### ``







