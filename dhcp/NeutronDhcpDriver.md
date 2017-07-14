# Neutron dhcp driver

在配置文件 */etc/neutron/dhcp_agent.ini* 中，我们看到默认的 dhcp agent driver 为：`dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq`

## `class Dnsmasq(DhcpLocalProcess)`

### `def check_version(cls)`

空方法

### `def existing_dhcp_networks(cls, conf)`

1. 调用 `get_confs_dir` 获取配置中 dhcp agent server 的配置文件的目录（这个目录下是一堆子目录，这些子目录都是以 network id 来命名的）
2. 读取下面的所有子目录名称（即所有使用该 dhcp agent 的网络 id）

### ``


















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














