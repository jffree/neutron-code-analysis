# Neutron dhcp driver

在配置文件 */etc/neutron/dhcp_agent.ini* 中，我们看到默认的 dhcp agent driver 为：`dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq`

## `class Dnsmasq(DhcpLocalProcess)`




## `class DhcpLocalProcess(DhcpBase)`



## `class DhcpBase(object)`

抽象基类，定义了 dhcp agent driver 的框架