# 转换到OpenStack客户端

本文档详细介绍了将 neutron 客户端的 OpenStack Networking API 支持（包括Python库和neutron 命令行界面（CLI））移植到 [OpenStack Client（OSC）](https://github.com/openstack/python-openstackclient) 和 [OpenStack Python SDK](https://github.com/openstack/python-openstacksdk) 的过渡路线图。这个转换由 [Deprecate individual CLIs in favour of OSC](https://review.openstack.org/#/c/243348/) OpenStack spec 引导。 请参阅 [neutron RFE](https://bugs.launchpad.net/neutron/+bug/1521291)，[OSC neutron support etherpad](https://etherpad.openstack.org/p/osc-neutron-support) 和以下详细信息，以了解此过渡的整体进度。

## 概述

这种过渡将导致 neutron 客户端的 `neutron` CLI被弃用，然后最终被去除。`neutron` CLI将由OSC通过 openstack CLI 提供的网络支持取代。 这与[keystone客户端](https://github.com/openstack/python-keystoneclient)的`keystone` CLI的弃用和删除过程类似。neutron 客户端的Python库不会被弃用。 它将在OpenStack Python SDK提供的网络支持旁边提供。

neutron 客户端命令扩展的用户需要在 `neutron` CLI被移除之前转换到OSC插件系统。 这样的用户将在他们自己的项目中维护他们的OSC插件命令，并且将负责弃用和删除它们的 neutron CLI扩展。

## 转移进度

1. **Done**: OSC adds OpenStack Python SDK as a dependency. See the following patch set: [https://review.openstack.org/\#/c/138745/](https://review.openstack.org/#/c/138745/)
2. **Done**: OSC switches its networking support for the network command object to use the OpenStack Python SDK instead of the neutron client’s Python library. See the following patch set: [https://review.openstack.org/\#/c/253348/](https://review.openstack.org/#/c/253348/)
3. **Done**: OSC removes its python-neutronclient dependency. See the following patch set: [https://review.openstack.org/\#/c/255545/](https://review.openstack.org/#/c/255545/)
4. **In Progress**: OpenStack Python SDK releases version 1.0 to guarantee backwards compatibility of its networking support and OSC updates its dependencies to include OpenStack Python SDK version 1.0 or later. See the following blueprint: [https://blueprints.launchpad.net/python-openstackclient/+spec/network-command-sdk-support](https://blueprints.launchpad.net/python-openstackclient/+spec/network-command-sdk-support)
5. **Done**: OSC switches its networking support for the ip floating, ip floating pool, ip fixed, security group, and security group rule command objects to use the OpenStack Python SDK instead of the nova client’s Python library when neutron is enabled. When nova network is enabled, then the nova client’s Python library will continue to be used. See the following OSC bugs:
   * **Done** Floating IP CRUD
   * **Done** Port CRUD
   * **Done** Security Group CRUD
   * **Done** Security Group Rule CRUD
6. **In Progress**: OSC continues enhancing its networking support. At this point and when applicable, enhancements to the neutron CLI must also be made to the openstack CLI and possibly the OpenStack Python SDK. Users of the neutron client’s command extensions should start their transition to the OSC plugin system. See the developer guide section below for more information on this step.
7. **In Progress**: Deprecate the neutron CLI. Running the CLI after it has been deprecated will issue a warning message: neutron CLI is deprecated and will be removed in the future. Use openstack CLI instead. In addition, no new features will be added to the CLI, though fixes to the CLI will be assessed on a case by case basis.
8. **Not Started**: Remove the neutron CLI after two deprecation cycles once the criteria below have been met.
   * The networking support provide by the openstack CLI is functionally equivalent to the neutron CLI and it contains sufficient functional and unit test coverage.
   * Neutron Stadium projects, Neutron documentation and DevStack use openstack CLI instead of neutron CLI.
   * Most users of the neutron client’s command extensions have transitioned to the OSC plugin system and use the openstack CLI instead of the neutron CLI.

## [开发者手册](https://docs.openstack.org/developer/python-neutronclient/devref/transition_to_osc.html#developer-guide)

neutron CLI版本6.x，没有扩展，支持超过200个命令，而openstack CLI版本3.3.0支持超过70个网络命令。 在70个命令中，有些没有 neutron CLI等效的所有选项或参数。 有了这个巨大的功能差距，开发人员在这个过渡期间的几个关键问题是 _“我改变了哪个CLI？”，“我的CLI在哪里？”_和_“我改变了哪个Python库”？_答案取决于状态的命令和整体过渡状态。 下表列出了详细情况。 过渡的初期阶段将需要双重维护。

_其余未翻译，请参考原文_

