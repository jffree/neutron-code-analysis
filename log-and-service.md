## 查看日志：

* 切换至 `stack`用户，输入如下命令：

```
$su - stack
$screen -x stack
```

`screen`_是一个终端复用器，类似于 _`tmux`。

_使用方法请参考：_[_linux screen 命令详解_](http://www.cnblogs.com/mchina/archive/2013/01/30/2880680.html)

## 服务管理：

使用 `devstack `部署完 `openstack `后可以发现，所有的 `openstack `服务都不是以 `service `的形式启动的，那么我们应该如何在重启机器的时候启动这些服务呢？

答案是：再次运行一遍 `./stack.sh`

之前的`devstack`版本中还有`rejoin-stack.sh`这个脚本，但是新的版本中将其移除了。

参考：[No rejoin-stack.sh script in my setup](http://stackoverflow.com/questions/36268822/no-rejoin-stack-sh-script-in-my-setup)



