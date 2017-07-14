## Port 的种类是如何区分的？

![](http://i1.wp.com/www.innervoice.in/blogs/wp-content/uploads/2015/07/Topology-OpenStack-Ports-1.png)

```
DEVICE_OWNER_COMPUTE_PREFIX
DEVICE_OWNER_NETWORK_PREFIX
DEVICE_OWNER_NEUTRON_PREFIX
DEVICE_OWNER_BAREMETAL_PREFIX
```

**参考：** [Ports in OpenStack Neutron](http://www.innervoice.in/blogs/2015/07/05/ports-in-openstack-neutron/)

## segment 的作用

* 如何开启 segment 服务？

segment service 是一个 service plugin，若是想要启动这个 plugin 需要在 *neutron.conf* 中的 `service_plugins` 选项后面增加 `segments`，然后重启 neutron-server

* segment 代表了什么？

当我们开启 segments service plugin 后，我们使用命令查看任意子网的信息：

```
neutron subnet-show private-subnet
```

```
+-------------------+--------------------------------------------+
| Field             | Value                                      |
+-------------------+--------------------------------------------+
| allocation_pools  | {"start": "10.0.0.2", "end": "10.0.0.254"} |
| cidr              | 10.0.0.0/24                                |
| created_at        | 2017-03-07T10:01:21Z                       |
| description       |                                            |
| dns_nameservers   |                                            |
| enable_dhcp       | True                                       |
| gateway_ip        | 10.0.0.1                                   |
| host_routes       |                                            |
| id                | f61f47d3-2396-4528-bc70-bf761b5753cc       |
| ip_version        | 4                                          |
| ipv6_address_mode |                                            |
| ipv6_ra_mode      |                                            |
| name              | private-subnet                             |
| network_id        | 534b42f8-f94c-4322-9958-2d1e4e2edd47       |
| project_id        | e2a6f26416654301a25f70e20892f1bc           |
| revision_number   | 2                                          |
| segment_id        |                                            |
| service_types     |                                            |
| subnetpool_id     |                                            |
| tenant_id         | e2a6f26416654301a25f70e20892f1bc           |
| updated_at        | 2017-03-07T10:01:21Z                       |
+-------------------+--------------------------------------------+
```

我们发现，返回的信息中多了一个 `segment_id` 的东东。

* 那么这个 `segment_id` 代表了什么呢？

这个 segment_id 代表了 `NetworkSegment` 数据库记录的 id。这个数据库代表了 segment 与 network 绑定的状态。

```
MariaDB [neutron]> desc networksegments;
+------------------+--------------+------+-----+---------+-------+
| Field            | Type         | Null | Key | Default | Extra |
+------------------+--------------+------+-----+---------+-------+
| id               | varchar(36)  | NO   | PRI | NULL    |       |
| network_id       | varchar(36)  | NO   | MUL | NULL    |       |
| network_type     | varchar(32)  | NO   |     | NULL    |       |
| physical_network | varchar(64)  | YES  |     | NULL    |       |
| segmentation_id  | int(11)      | YES  |     | NULL    |       |
| is_dynamic       | tinyint(1)   | NO   |     | 0       |       |
| segment_index    | int(11)      | NO   |     | 0       |       |
| standard_attr_id | bigint(20)   | NO   | UNI | NULL    |       |
| name             | varchar(255) | YES  |     | NULL    |       |
+------------------+--------------+------+-----+---------+-------+
```

还有一个数据库 `SegmentHostMapping`，这个数据库代表了 segment 与 host 的绑定状态。这个数据库里面的 `segment_id` 同样也是 `NetworkSegment` 数据库记录的 id。

```
MariaDB [neutron]> desc segmenthostmappings;
+------------+--------------+------+-----+---------+-------+
| Field      | Type         | Null | Key | Default | Extra |
+------------+--------------+------+-----+---------+-------+
| segment_id | varchar(36)  | NO   | PRI | NULL    |       |
| host       | varchar(255) | NO   | PRI | NULL    |       |
+------------+--------------+------+-----+---------+-------+
```

* 这样子串起来，我们就明白了：

1. subnet 可以和 segment 绑定
2. host 可以和 segment 绑定
3. 那么只有当 subnet 和 host 的 segment 一致时，该 subnet 才可以被该 host 上的 dhcp agent 调度。我们称这样的机制为 `routing`。
4. 那么最终我们会将 segment 一致的 network 与 dhcp agent 进行绑定，也就是创建 `NetworkDhcpAgentBinding` 的数据库记录。