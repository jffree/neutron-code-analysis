# python OVS 之 socket_util

*ovs/socket_util.py*

用于 ovs socket 连接的辅助模块。

## `def inet_parse_active(target, default_port)`

作用：返回目标主机的地址和端口。（例如：`('127.0.0.1', 6640)`）

* 参数说明：
 * `target`：目标主机地址（可能包含端口）（例如：`'127.0.0.1:6640'`）；
 * `default_pot`：默认目标主机的端口，在 target 未包含端口的情况下使用。

## `def inet_open_active(style, target, default_port, dscp)`

* 参数说明：
 * `style`： socket 类型
 * `target`：目标主机的地址
 * `default_port`：默认的目标主机端口
 * `dscp`：TOS 值。

1. 创建一个 AF_INET 地址簇的 socket（`socket.socket(socket.AF_INET, style, 0)`）
2. 将套接字设置为非阻塞模式
3. 设置 socket 的 TOS 值。
4. 连接到 target 处的套接字。


参考：[ python socket编程详细介绍 ](http://yangrong.blog.51cto.com/6945369/1339593)

## `def is_valid_ipv4_address(address)`

判断一个地址是否为有效的 Ipv4 地址

## `def set_nonblocking(sock)`

将 socket 设置为非阻塞模式。

## `def set_dscp(sock, family, dscp)`

设定 socket 的 TOS 值（`dscp`）。

## `def check_connection_completion(sock)`



































