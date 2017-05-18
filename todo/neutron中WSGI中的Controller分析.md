# Neutron 中 WSGI Controller 分析

## `create`

1. 使用 `_notifier` 发送消息
2. 调用 `_create` 方法

## `_create`

1. 获取父类资源的id
2. 调用 `prepare_request_body` 方法进行检查工作
3. 获取 `_plugin` 中的具体实现方法

## `prepare_request_body`

* 对用户请求的数据（消息体）做检查、填充默认数据的工作。