# ovs 使用总结

## 设置了 tag 的 Port 与不设置 tag 的 port 之间的数据包流通

* 情景建立： 

```
ovs-vsctl add-br br0
ovs-vsctl add-port br0 p1
ovs-vsctl add-port br0 p2
ovs-vsctl add-port br0 p3
ovs-vsctl set Port p2 tag=10
ovs-vsctl set Port p3 tag=11
```

1. 从 p1 进入的数据包无法转发到 p2、p3 上面
2. 从 p2、p3 进入的数据包可以转发到 p1 上面
3. 从 p2 进入的数据包不可转发到 p3 上面












