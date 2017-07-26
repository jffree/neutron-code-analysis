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

### `def spawn_process(self)`

```
    def spawn_process(self):
        """Spawn the process, if it's not spawned already."""
        # we only need to generate the lease file the first time dnsmasq starts
        # rather than on every reload since dnsmasq will keep the file current
        self._output_init_lease_file()
        self._spawn_or_reload_process(reload_with_HUP=False)
```

运行 dnsmasq 进程，为该 network 提供 dhcp 服务

1. 调用 `_output_init_lease_file` 创建 lease 文件
2. 调用 `_spawn_or_reload_process` 启动 dnsmasq 进程

### `def _output_init_lease_file(self)`

为该 dnsmasq 进行创建 lease file（租期维护文件），该文件用于 dnsmasq 的 `--dhcp-leasefile` 选项。

```
[root@CentOS-7 neutron]# cat /opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/leases 
1501085997 fa:16:3e:89:34:a4 10.0.0.1 host-10-0-0-1 *
1501085997 fa:16:3e:4f:27:12 192.168.200.2 host-192-168-200-2 *
1501085997 fa:16:3e:4f:27:12 192.168.100.2 host-192-168-100-2 *
1501085997 fa:16:3e:4f:27:12 10.0.0.2 host-10-0-0-2 *
```

### `def _spawn_or_reload_process(self, reload_with_HUP)`

1. 调用 `_output_config_files` 生成 hosts、addn_hosts、opts 文件
2. 以 `_build_cmdline_callback` 为 `cmd_callback` 创建 dnsmasq 的包装管理程序 pm（`ProcessManager` 的实例）
3. 启动 dnsmasq 进程，并注册监听

### `def _iter_hosts(self)`

根据网络上的端口，提供该 port 的 host 信息。

### `def _sort_fixed_ips_for_dnsmasq(self, fixed_ips, v6_nets)`

处理 dnsmasq 关于 ipv6 的一个问题

### `def _format_address_for_dnsmasq(address)`

对于 ipv6 格式的地址要区别对待

### `def _output_config_files(self)`

产生 dnsmasq 的配置文件

```
    def _output_config_files(self):
        self._output_hosts_file()
        self._output_addn_hosts_file()
        self._output_opts_file()
```

### `def _output_hosts_file(self)`

创建 hosts 文件。在 dnsmasq 的 `--dhcp-hostsfile` 选项中用到。

```
[root@CentOS-7 neutron]# cat /opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/host 
fa:16:3e:4f:27:12,host-10-0-0-2.openstacklocal,10.0.0.2
fa:16:3e:4f:27:12,host-192-168-100-2.openstacklocal,192.168.100.2
fa:16:3e:4f:27:12,host-192-168-200-2.openstacklocal,192.168.200.2
fa:16:3e:89:34:a4,host-10-0-0-1.openstacklocal,10.0.0.1
```

### `def _output_addn_hosts_file(self)`

创建 addn_hosts 文件。在 dnsmasq 的 `--addn-hosts` 选项中用到。

```
[root@CentOS-7 neutron]# cat /opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/addn_hosts 
fd28:f82d:79fd::1	host-fd28-f82d-79fd--1.openstacklocal host-fd28-f82d-79fd--1
10.0.0.2	host-10-0-0-2.openstacklocal host-10-0-0-2
192.168.100.2	host-192-168-100-2.openstacklocal host-192-168-100-2
192.168.200.2	host-192-168-200-2.openstacklocal host-192-168-200-2
fd28:f82d:79fd:0:f816:3eff:fe4f:2712	host-fd28-f82d-79fd-0-f816-3eff-fe4f-2712.openstacklocal host-fd28-f82d-79fd-0-f816-3eff-fe4f-2712
10.0.0.1	host-10-0-0-1.openstacklocal host-10-0-0-1
```

### `def _output_opts_file(self)`

创建 opts 文件。在 dnsmasq 的 `--dhcp-optsfile` 选项中用到。

```
[root@CentOS-7 neutron]# cat /opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/opts 
tag:tag1,option:classless-static-route,192.168.200.0/24,0.0.0.0,10.0.0.0/24,0.0.0.0,0.0.0.0/0,192.168.100.1
tag:tag1,249,192.168.200.0/24,0.0.0.0,10.0.0.0/24,0.0.0.0,0.0.0.0/0,192.168.100.1
tag:tag1,option:router,192.168.100.1
tag:tag2,option:classless-static-route,192.168.100.0/24,0.0.0.0,10.0.0.0/24,0.0.0.0,0.0.0.0/0,192.168.200.1
tag:tag2,249,192.168.100.0/24,0.0.0.0,10.0.0.0/24,0.0.0.0,0.0.0.0/0,192.168.200.1
tag:tag2,option:router,192.168.200.1
tag:tag3,option:classless-static-route,169.254.169.254/32,10.0.0.1,192.168.100.0/24,0.0.0.0,192.168.200.0/24,0.0.0.0,0.0.0.0/0,10.0.0.1
tag:tag3,249,169.254.169.254/32,10.0.0.1,192.168.100.0/24,0.0.0.0,192.168.200.0/24,0.0.0.0,0.0.0.0/0,10.0.0.1
```

### `def _build_cmdline_callback(self, pid_file)`

构建执行 dnsmasq 的命令。

例如：

```
dnsmasq --no-hosts  --strict-order --except-interface=lo --pid-file=/opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/pid --dhcp-hostsfile=/opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/host --addn-hosts=/opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/addn_hosts --dhcp-optsfile=/opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/opts --dhcp-leasefile=/opt/stack/data/neutron/dhcp/fc066cb7-ade6-43bc-8221-fd9139d918b8/leases --dhcp-match=set:ipxe,175 --bind-interfaces --interface=tap921f5a37-3b --dhcp-range=set:tag1,192.168.100.0,static,86400s --dhcp-range=set:tag2,192.168.200.0,static,86400s --dhcp-range=set:tag3,10.0.0.0,static,86400s --dhcp-option-force=option:mtu,1450 --dhcp-lease-max=768 --conf-file= --domain=openstacklocal
```

### `def reload_allocations(self)`

1. 调用 `_release_unused_leases` 释放当前 network 中未使用的 ip
2. 调用 `_spawn_or_reload_process` 以发送 `HUP` 的方式重新运行（SIGHUP 信号会让 dnsmasq 进程重新加载配置）
3. 重新对该进程进行监测

### `def _release_unused_leases(self)`

根据 network 中现有的 port 信息，调用 `_release_lease` 释放那些未使用的 ip 

### `def _read_hosts_file_leases(self, filename)`

读取 hosts 文件的数据 `(ip, mac, client_id)`

### `def _read_v6_leases_file_leases(self, filename)`

读取 leases 文件中 ipv6 的相关信息（`(iaid, ip, client_id)`）

### `def _get_client_id(self, port)`

读取 port 的 client_id 属性

### `def _release_lease(self, mac_address, ip, client_id=None, server_id=None, iaid=None)`

1. 若 Ip 为 v6 版本，则首先调用 `_is_dhcp_release6_supported` 检查是否支持 `dhcp_release6` 命令，若不支持则返回。若支持，则调用 `dhcp_release6` 命令释放该 ip 地址。
2. 若 Ip 为 v4 版本，则直接调用 `dhcp_release` 释放该 ip 









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

### `def _get_process_manager(self, cmd_callback=None)`

构造一个子进程的包装（`ProcessManager`）实例

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

### `def _remove_config_files(self)`

删除该 network dhcp 的所有数据文件

### `def enable(self)`

```

        if self.active:
            self.restart()
        elif self._enable_dhcp():
            common_utils.ensure_dir(self.network_conf_dir)
            interface_name = self.device_manager.setup(self.network)
            self.interface_name = interface_name
            self.spawn_process()
```

* 根据子进程（dnsmasq）的 pid 是否存在，判断 dnsmasq 命令是否运行
 1. 若子进程已经运行，则调用 `restart` 方法
 2. 若子进程还未运行，则进行下面几步操作：
  1. 在 neutron dhcp 数据目录下面建立以该 network id 命名的子目录（这个会在 `__init__`方法里面建立，这里只是检查）
  2. 调用 `DeviceManager.setup` 方法为该 network 准备好提供 dhcp 服务的网卡
  3. 调用 `spawn_process`（在子类中实现）启动 dnsmasq 命令

### `def disable(self, retain_port=False)`

1. 调用 `process_monitor.unregister` 去掉对该 network 提供 dhcp 服务的进程 dnsmasq 的监测
2. 调用 `ProcessManager.disable` 停掉该 dnsmasq 进程
3. 调用 `_destroy_namespace_and_port` 删除掉该 network 的 namspace 和 网络设备
4. 调用 `_remove_config_files` 删除数据目录下与该 network 相关的所有文件




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

### `def restart(self)`

```
    def restart(self):
        """Restart the dhcp service for the network."""
        self.disable(retain_port=True)
        self.enable()
```













## `class DeviceManager(object)`

### `def __init__(self, conf, plugin)`

```
    def __init__(self, conf, plugin):
        self.conf = conf
        self.plugin = plugin
        self.driver = agent_common_utils.load_interface_driver(conf)
```

* `plugin`：负责与 neutron-server 通讯的 RPC Client，`DhcpPluginApi` 的实例

调用 `agent_common_utils.load_interface_driver` 加载实际的 interface driver。
dhcp agent interface dirver 在 *dhcp_agent.ini* 中定义：`interface_driver = openvswitch`。
在 *setup.cfg* 中，可以看到这驱动对应的模块为：

```
    openvswitch = neutron.agent.linux.interface:OVSInterfaceDriver
```

### `def setup(self, network)`

1. 调用 `setup_dhcp_port` 创建为该 network 提供 dhcp 服务的网卡
2. 调用 `_update_dhcp_port` 更新新创建的 port 在 network 中的信息
3. 调用 `get_interface_name` 获取该 port 在 linux 上的名称
4. 调用 `ip_lib.ensure_device_is_ready` 确保该 port 已经被激活。若 `ip_lib.ensure_device_is_ready` 无法完成操作，则调用 `plug` 方法完成。
5. 调用 `fill_dhcp_udp_checksums` 填充目的端口为68的udp报文的checksum改为fill 
6. 调用 `driver.init_l3` 为该网卡设置 ip 地址
7. 调用 `_set_default_route` 为该 port 设定路由信息
8. 调用 `_cleanup_stale_devices` 清除该网络 namesapce 中其他所有的 port（只保留 lo 和刚才构建的用于提供 dhcp 服务的 port）。

### `def setup_dhcp_port(self, network)`

作用：创建（更新）为 network 的 dhcp 服务的 port。

1. 调用 `get_device_id` 获取一个独一无二的 device id
2. 获取该网络下允许 dhcp 服务的 subnet
3. 对于一个网络来说，dhcp port 有三种情况：第一是已经存在了（`_setup_existing_dhcp_port`）；第二是被用户手动创建的（`_setup_reserved_dhcp_port`）；第三是还未创建（`_setup_new_dhcp_port`）。本方法会依次处理这三种情况。
4. 调用 `_setup_existing_dhcp_port` 检查否已经存在了为该 network 提供 dhcp 服务的网卡
5. 调用 `_setup_reserved_dhcp_port` 检查是否有预留的 port
6. 调用 `_setup_new_dhcp_port` 创建新的 port
7. 检查 port 上是否含有所有提供 dhcp 服务的 subnet 的 ip 地址
8. 用 `DictModel` 封装该 port 的 ip 信息。
9. 返回该 port 的信息

### `def get_device_id(self, network)`

调用 `common_utils.get_dhcp_agent_device_id` 创建一个 device id（在 network、host 一定的情况下，device id 也是一定的）

### `def _setup_existing_dhcp_port(self, network, device_id, dhcp_subnets)`

* 检查该 network 中是否已经提供 dhcp 服务的网卡

1. 若未预留则返回空
2. 若预留了 port，但是该 port 上没有希望进行提供 dhcp 服务的 subnet 中的 ip 地址，则会通过调用 RPC Server 的 `update_dhcp_port` 方法，来为该 port 增加新的 ip 地址。返回 port

### `def _setup_reserved_dhcp_port(self, network, device_id, dhcp_subnets)`

* 检查该 network 中是否预留了为提供 dhcp 服务的网卡（`port_device_id == n_const.DEVICE_ID_RESERVED_DHCP_PORT`）

1. 若存在预留，则更新该 port 的 device_id
2. 若不存在预留则直接退出

### `def _setup_new_dhcp_port(self, network, device_id, dhcp_subnets)`

* 通过调用 RPC Server 端的 `create_dhcp_port` 创建为该 network 提供 dhcp 服务的 port。

### `def _update_dhcp_port(self, network, port)`

更新该 port 在 network 中的数据信息。

### `def get_interface_name(self, network, port)`

通过调用 `driver.get_device_name` 获取该 port 在 Linux 上的名称（*tap921f5a37-3b*）

### `def plug(self, network, port, interface_name)`

调用 `driver.plug` 实现

### `def fill_dhcp_udp_checksums(self, namespace)`

执行 `ip netns exec qdhcp-fc066cb7-ade6-43bc-8221-fd9139d918b8 iptables -A POSTROUTING -t mangle -p udp --dport 68 -j CHECKSUM --checksum-fill` 命令

### `def _set_default_route(self, network, device_name)`

为该网络设备设定默认的 route。默认的 route 只会设置一个（从 network 的 subnet 中选取）。

若该 dhcp port 之前的默认 route 不再属于当前 subnet 的范畴，则将其删除，增加新的默认 gateway。

```
[root@CentOS-7 ~]# ip netns exec qdhcp-fc066cb7-ade6-43bc-8221-fd9139d918b8 ip route
default via 192.168.100.1 dev tap921f5a37-3b 
10.0.0.0/24 dev tap921f5a37-3b  proto kernel  scope link  src 10.0.0.2 
192.168.100.0/24 dev tap921f5a37-3b  proto kernel  scope link  src 192.168.100.2 
192.168.200.0/24 dev tap921f5a37-3b  proto kernel  scope link  src 192.168.200.2
```

启动 `default via 192.168.100.1 dev tap921f5a37-3b` 即为默认的 route。

### `def _cleanup_stale_devices(self, network, dhcp_port)`

清除该网络 namesapce 中其他所有的 port（只保留 lo 和刚才构建的用于提供 dhcp 服务的 port）

### `def destroy(self, network, device_name)`

1. 调用 `unplug` 方法删除名为 device_name 的设备
2. 通过 RPC 调用 Server 端的 `release_dhcp_port` 方法删除该 port 在 neutron-server 数据库中的记录
 
### `def unplug(self, device_name, network)`

调用 dhcp interface driver 的 `unplug` 方法实现

### ``







