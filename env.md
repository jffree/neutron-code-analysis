## sys.path

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



