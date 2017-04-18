# Neutron 中 plugin 和 extension 的加载流程

主要参考：[JUNO NEUTRON中的plugin和extension介绍及加载机制](http://bingotree.cn/?p=660&utm_source=tuicool&utm_medium=referral)

## 预备知识

* wsgi

 * 请参考我收集的关于 wsgi 的资料

* neutron_lib

* oslo_service

* stevedore

 *  [Python深入：stevedore简介](http://blog.csdn.net/gqtcgq/article/details/49620279)
 * [stevedore – Manage Dynamic Plugins for Python Applications](https://docs.openstack.org/developer/stevedore/)  
 
## 分析流程

### api-paste.ini 文件

根据 paste.deploy 的相关知识，我们可以知道，访问 neutron 的 wsgi 服务的的入口点如下：

```
[composite:neutron]
use = egg:Paste#urlmap
/: neutronversions_composite
/v2.0: neutronapi_v2_0
```