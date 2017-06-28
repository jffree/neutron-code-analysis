# Neutron Qos db 访问

*neutron/db/qos/api.py*

## `def create_policy_network_binding(context, policy_id, network_id)`

创建一个 qos policy 与 network 的绑定记录

## `def delete_policy_network_binding(context, policy_id, network_id)`

删除 qos policy 与 network 的绑定记录

## `def get_network_ids_by_network_policy_binding(context, policy_id)`

检查都有哪些 network 与 qos policy 绑定

## `def create_policy_port_binding(context, policy_id, port_id)`

创建一个 qos policy 与 port 的绑定记录

## `def delete_policy_port_binding(context, policy_id, port_id)`

删除 qos policy 与 port 的绑定记录

## `def get_port_ids_by_port_policy_binding(context, policy_id)`

检查都有哪些 port 与 qos policy 绑定