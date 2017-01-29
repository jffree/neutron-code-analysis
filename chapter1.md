## 环境

1. 操作系统为：`centos7`
2. `openstack`版本为：`newton`

## 部署步骤

* 安装相关软件

```
#yum install -y git python-pip 
```

* '克隆 `devstack`库

```
#cd /opt
#git clone https://github.com/openstack-dev/devstack.git -b stable/newton
```

* 创建 `stack`用户，修改用户目录权限

```
#cd /opt/devstack
#./tools/create-stack-user.sh
#chown -R stack:stack /opt/devstack
```

* 切换至 `stack `用户，编写`local.conf`文件

```
#su - stack
$cd /opt/devstack
$vim local.conf
```

> \[\[local\|localrc\]\]
>
>
>
> \# use TryStack git mirror
>
> GIT\_BASE=http://git.trystack.cn
>
> NOVNC\_REPO=http://git.trystack.cn/kanaka/noVNC.git
>
> SPICE\_REPO=http://git.trystack.cn/git/spice/spice-html5.git
>
>
>
> \# Credentials
>
> DATABASE\_PASSWORD=abc123
>
> ADMIN\_PASSWORD=abc123
>
> SERVICE\_PASSWORD=abc123
>
> SERVICE\_TOKEN=abc123
>
> RABBIT\_PASSWORD=abc123

* 开始部署

```
$ ./stack.sh
```

**若是部署过程中出现问题，可执行 `./unstack.sh` 清理，完后再次重新部署。**



使用 `devstack`部署完`openstack` 之后，所有相关的库都被安装在 `/opt/stack` 下，通过在 `site-packages` 中的 `easy-install.pth` 加入到 `sys.path` 中：

```
import sys; sys.__plen = len(sys.path)
/opt/stack/keystone
/opt/stack/glance
/opt/stack/cinder
/opt/stack/neutron
/opt/stack/nova
/opt/stack/horizon
/opt/stack/tempest
import sys; new = sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p = getattr(sys, '__egginsert', 0); sys.path[p:p] = new; sys.__egginsert = p + len(new)
```



