# Neutron dhcp manager

dhcp agent 是以一个 service 的方式启动。其实就是以 dhcp manger 为 endpoint 启动一个 rpc server。（请见文章：neutron中的Service）

dhcp agent 的 manager 为：`neutron.agent.dhcp.agent.DhcpAgentWithStateReport`