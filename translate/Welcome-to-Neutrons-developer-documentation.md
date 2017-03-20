# Welcome to Neutron’s developer documentation!

Neutron是在由其他OpenStack服务（例如，nova）管理的接口设备（例如，vNIC）之间提供“网络连接作为服务”的OpenStack项目。它实现了[Neutron API](http://docs.openstack.org/api/openstack-network/2.0/content/)。

本文档介绍了Neutron对openstack的贡献，并假设您已经从终端熟悉Neutron。

此文档由Sphinx工具包生成，并且位于源代码树中。 有关Neutron和OpenStack的其他组件的其他文档可以在[OpenStack wiki](http://wiki.openstack.org/)和Wiki的Neutron部分找到。[Neutron Development wiki](http://wiki.openstack.org/NeutronDevelopment)对新贡献者来说也是一个好资源。

## Neutron Policies

* [Neutron Policies](https://docs.openstack.org/developer/neutron/policies/index.html)
 * [Blueprints and Specs](https://docs.openstack.org/developer/neutron/policies/blueprints.html)
 * [Neutron Bugs](https://docs.openstack.org/developer/neutron/policies/bugs.html)
 * [Contributor Onboarding](https://docs.openstack.org/developer/neutron/policies/contributor-onboarding.html)
 * [Neutron Core Reviewers](https://docs.openstack.org/developer/neutron/policies/neutron-teams.html)
 * [Neutron Teams](https://docs.openstack.org/developer/neutron/policies/neutron-teams.html#neutron-teams)
 * [Code Merge Responsibilities](https://docs.openstack.org/developer/neutron/policies/neutron-teams.html#code-merge-responsibilities)
 * [Neutron Gate Failure Triage](https://docs.openstack.org/developer/neutron/policies/gate-failure-triage.html)
 * [Neutron Code Reviews](https://docs.openstack.org/developer/neutron/policies/code-reviews.html)
 * [Pre-release check list](https://docs.openstack.org/developer/neutron/policies/release-checklist.html)
 * [Neutron Third-party CI](https://docs.openstack.org/developer/neutron/policies/thirdparty-ci.html)

## Neutron Stadium

* [Neutron Stadium](https://docs.openstack.org/developer/neutron/stadium/index.html)
 * [Stadium Governance](https://docs.openstack.org/developer/neutron/stadium/governance.html)
 * [Sub-Project Guidelines](https://docs.openstack.org/developer/neutron/stadium/guidelines.html)

## Developer Docs

* [Developer Guide](https://docs.openstack.org/developer/neutron/devref/index.html)
 * [Programming HowTos and Tutorials](https://docs.openstack.org/developer/neutron/devref/index.html)
   * [Effective Neutron: 100 specific ways to improve your Neutron contributions](https://docs.openstack.org/developer/neutron/devref/effective_neutron.html)
   * [Setting Up a Development Environment](https://docs.openstack.org/developer/neutron/devref/development.environment.html)
   * [Testing Neutron](https://docs.openstack.org/developer/neutron/devref/development.environment.html)
   * [Contributing new extensions to Neutron](https://docs.openstack.org/developer/neutron/devref/contribute.html)
   * [Neutron public API](https://docs.openstack.org/developer/neutron/devref/neutron_api.html)
   * [Client command extension support](https://docs.openstack.org/developer/neutron/devref/client_command_extensions.html)
   * [Alembic Migrations](https://docs.openstack.org/developer/neutron/devref/alembic_migrations.html)
 * [Neutron Internals](https://docs.openstack.org/developer/neutron/devref/index.html#neutron-internals)
   * [Services and agents](https://docs.openstack.org/developer/neutron/devref/services_and_agents.html)
   * [Neutron WSGI/HTTP API layer](https://docs.openstack.org/developer/neutron/devref/api_layer.html)
   * [ML2 Extension Manager](https://docs.openstack.org/developer/neutron/devref/ml2_ext_manager.html)
   * [Calling the ML2 Plugin](https://docs.openstack.org/developer/neutron/devref/calling_ml2_plugin.html)
   * [Quota Management and Enforcement](https://docs.openstack.org/developer/neutron/devref/quota.html)
   * [API Extensions](https://docs.openstack.org/developer/neutron/devref/api_extensions.html)
   * [Neutron Plugin Architecture](https://docs.openstack.org/developer/neutron/devref/plugin-api.html)
   * [Neutron Database Layer](https://docs.openstack.org/developer/neutron/devref/db_layer.html)
   * [Relocation of Database Models](https://docs.openstack.org/developer/neutron/devref/db_models.html)
   * [Authorization Policy Enforcement](https://docs.openstack.org/developer/neutron/devref/policy.html)
   * [Neutron RPC API Layer](https://docs.openstack.org/developer/neutron/devref/rpc_api.html)
   * [Neutron Messaging Callback System](https://docs.openstack.org/developer/neutron/devref/rpc_callbacks.html)
   * [Layer 3 Networking in Neutron - via Layer 3 agent & OpenVSwitch](https://docs.openstack.org/developer/neutron/devref/layer3.html)
   * [L3 agent extensions](https://docs.openstack.org/developer/neutron/devref/layer3.html#l3-agent-extensions)
   * [L2 Agent Networking](https://docs.openstack.org/developer/neutron/devref/l2_agents.html)
   * [Agent extensions](https://docs.openstack.org/developer/neutron/devref/agent_extensions.html)
   * [Neutron Open vSwitch vhost-user support](https://docs.openstack.org/developer/neutron/devref/ovs_vhostuser.html)
   * [Quality of Service](https://docs.openstack.org/developer/neutron/devref/quality_of_service.html)
   * [Service Extensions](https://docs.openstack.org/developer/neutron/devref/service_extensions.html)
   * [Neutron Callback System](https://docs.openstack.org/developer/neutron/devref/callbacks.html)
   * [Keep DNS Nameserver Order Consistency In Neutron](https://docs.openstack.org/developer/neutron/devref/dns_order.html)
   * [Integration with external DNS services](https://docs.openstack.org/developer/neutron/devref/external_dns_integration.html)
   * [Upgrade strategy](https://docs.openstack.org/developer/neutron/devref/upgrade.html)
   * [Objects in neutron](https://docs.openstack.org/developer/neutron/devref/objects_usage.html)
   * [Neutron Stadium i18n](https://docs.openstack.org/developer/neutron/devref/i18n.html)
   * [Subnet Pools and Address Scopes](https://docs.openstack.org/developer/neutron/devref/address_scopes.html)
   * [Open vSwitch Firewall Driver](https://docs.openstack.org/developer/neutron/devref/openvswitch_firewall.html)
   * [Network IP Availability Extension](https://docs.openstack.org/developer/neutron/devref/network_ip_availability.html)
   * [Add Tags to Neutron Resources](https://docs.openstack.org/developer/neutron/devref/tag.html)
   * [Composite Object Status via Provisioning Blocks](https://docs.openstack.org/developer/neutron/devref/provisioning_blocks.html)
   * [Retrying Operations](https://docs.openstack.org/developer/neutron/devref/retries.html)
   * [L3 agent extensions](https://docs.openstack.org/developer/neutron/devref/l3_agent_extensions.html)
 * [Testing](https://docs.openstack.org/developer/neutron/devref/index.html#testing)
   * [Full Stack Testing](https://docs.openstack.org/developer/neutron/devref/fullstack_testing.html)
   * [Test Coverage](https://docs.openstack.org/developer/neutron/devref/testing_coverage.html)
   * [Template for ModelMigrationSync for external repos](https://docs.openstack.org/developer/neutron/devref/template_model_sync_test.html)
   * [Transient DB Failure Injection](https://docs.openstack.org/developer/neutron/devref/db_transient_failure_injection.html)
 * [Module Reference](https://docs.openstack.org/developer/neutron/devref/index.html#module-reference)
 * [Indices and tables](https://docs.openstack.org/developer/neutron/devref/index.html#module-reference)

## Dashboards

有一个dashboard的集合，以帮助位于这里的开发人员和审阅者。

* [Gerrit Dashboards](https://docs.openstack.org/developer/neutron/dashboards/index.html)
* [Grafana Dashboards](https://docs.openstack.org/developer/neutron/dashboards/index.html#grafana-dashboards)

## API 扩展

有关OpenStack Network API扩展的信息，请访问[http://api.openstack.org](http://api.openstack.org)。
















































