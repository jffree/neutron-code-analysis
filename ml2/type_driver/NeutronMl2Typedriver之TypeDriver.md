# Neutron Ml2 typedriver 之 TypeDriver

*neutron/plugins/ml2/driver_api.py*

type driver 的抽象基类，定义了 type driver 的框架。

## `def get_type(self)`

## `def initialize(self)`

## `def is_partial_segment(self, segment)`

## `def validate_provider_segment(self, segment)`

## `def reserve_provider_segment(self, session, segment)`

## `def allocate_tenant_segment(self, session)`

## `def release_segment(self, session, segment)`

## `def get_mtu(self, physical)`