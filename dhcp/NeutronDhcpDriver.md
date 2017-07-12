# Neutron dhcp driver

在配置文件 */etc/neutron/dhcp_agent.ini* 中，我们看到默认的 dhcp agent driver 为：`dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq`

## `class Dnsmasq(DhcpLocalProcess)`


### `def check_version(cls)`

空方法

### `def existing_dhcp_networks(cls, conf)`

1. 调用 `get_confs_dir` 获取配置中 dhcp agent server 的配置文件的目录（这个目录下是一堆子目录，这些子目录都是以 network id 来命名的）
2. 读取下面的所有子目录名称（即所有使用该 dhcp agent 的网络 id）
3. 以 `NetModel` 来描述上一步获取网络资源（`id`） `net = dhcp.NetModel({"id": net_id, "subnets": [], "ports": []})`并保存在 cache 中

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

看到了什么：** init 方法会在 dhcp agent server 的配置目录下创建新的子目录，并且这些子目录都是以 network id 来命名的。**

### `def get_confs_dir(conf)`

根据配置信息中的 dhcp server 配置文件所在的目录（在 */etc/neutron/dhcp_agent.ini* 中：`dhcp_confs = $state_path/dhcp`）并将其转化为据对路径。




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