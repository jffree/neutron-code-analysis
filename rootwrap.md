### 简介：

使用rootwrap的目的就是针对系统某些特定的操作，让非特权用户以root用户的身份来安全地执行这些操作。openstack 曾经使用sudoers文件来列出允许执行的特权命令，使用sudo来运行这些命令，但是这样做不容易维护，而且不能进行复杂的参数处理。

### 实现及使用：

_不止是 neutron，nova、cinder中用到了 rootwrap 都是如此使用和实现的。_

* **在 setup.py 中我们可以看到定义的 neutron-server 的脚本接口以及单独存在的脚本文件：**

```
......
scripts = 
    bin/neutron-rootwrap
.....

neutron-rootwrap = oslo.rootwrap.cmd:main
.......
```

* **在 **`/etc/sudoers.d/`** 目录下增加一个 **`neutron-rootwrap`** 文件 ，其内容为：**

```
stack ALL=(root) NOPASSWD: /usr/bin/neutron-rootwrap /etc/neutron/rootwrap.conf *
stack ALL=(root) NOPASSWD: /usr/bin/neutron-rootwrap-daemon /etc/neutron/rootwrap.conf
```

_该文件的作用就是 stack 用户可以以无密码的方式执行 _`/usr/bin/neutron-rootwrap /etc/neutron/rootwrap.conf *`_  
 命令_

* `/etc/neutron/rootwrap.conf`** 定义了 rootwrap 的配置信息**

```
# Configuration for neutron-rootwrap
# This file should be owned by (and only-writeable by) the root user

[DEFAULT]
# List of directories to load filter definitions from (separated by ',').
# These directories MUST all be only writeable by root !
filters_path=/etc/neutron/rootwrap.d

# List of directories to search executables in, in case filters do not
# explicitely specify a full path (separated by ',')
# If not specified, defaults to system PATH environment variable.
# These directories MUST all be only writeable by root !
exec_dirs=/sbin,/usr/sbin,/bin,/usr/bin,/usr/local/bin,/usr/local/sbin,/usr/local/bin

# Enable logging to syslog
# Default value is False
use_syslog=False

# Which syslog facility to use.
# Valid values include auth, authpriv, syslog, local0, local1...
# Default value is 'syslog'
syslog_log_facility=syslog

# Which messages to log.
# INFO means log all usage
# ERROR means only log unsuccessful attempts
syslog_log_level=ERROR

[xenapi]
# XenAPI configuration is only required by the L2 agent if it is to
# target a XenServer/XCP compute host's dom0.
xenapi_connection_url=<None>
xenapi_connection_username=root
xenapi_connection_password=<None>
```

* 配置文件中的 `filters_path`定义了可以使用 rootwrap 的命令的过滤文件的目录

```
$ls /etc/neutron/rootwrap.d/
debug.filters  dibbler.filters   ipset-firewall.filters     l3.filters                  netns-cleanup.filters
dhcp.filters   ebtables.filters  iptables-firewall.filters  linuxbridge-plugin.filters  openvswitch-plugin.filters
```

_若是你有想要以 root 身份执行的命令可以在这里面增加文件，并写清楚你要执行的命令即可。_

* filters 文件的书写格式：

```
[filters]
cmd-name: filter-name, raw-command, user, args
```

源码分析：

[http://blog.csdn.net/gaoxingnengjisuan/article/details/47102593](http://blog.csdn.net/gaoxingnengjisuan/article/details/47102593)

[https://wiki.openstack.org/wiki/Rootwrap](https://wiki.openstack.org/wiki/Rootwrap)

[http://lingxiankong.github.io/blog/2014/03/11/rootwrap-in-openstack/](http://lingxiankong.github.io/blog/2014/03/11/rootwrap-in-openstack/)

