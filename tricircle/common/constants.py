# Copyright 2015 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# service type
ST_NOVA = 'nova'
# only support cinder v2
ST_CINDER = 'cinderv2'
ST_NEUTRON = 'neutron'
ST_GLANCE = 'glance'

# resource_type
RT_SERVER = 'server'
RT_VOLUME = 'volume'
RT_BACKUP = 'backup'
RT_SNAPSHOT = 'snapshot'
RT_NETWORK = 'network'
RT_SUBNET = 'subnet'
RT_PORT = 'port'
RT_ROUTER = 'router'

# version list
NOVA_VERSION_V21 = 'v2.1'
CINDER_VERSION_V2 = 'v2'
NEUTRON_VERSION_V2 = 'v2'

# supported release
R_LIBERTY = 'liberty'
R_MITAKA = 'mitaka'

# l3 bridge networking elements
ew_bridge_subnet_pool_name = 'ew_bridge_subnet_pool'
ew_bridge_net_name = 'ew_bridge_net_%s'  # project_id
ew_bridge_subnet_name = 'ew_bridge_subnet_%s'  # project_id
ew_bridge_port_name = 'ew_bridge_port_%s_%s'  # project_id b_router_id

ns_bridge_subnet_pool_name = 'ns_bridge_subnet_pool'
ns_bridge_net_name = 'ns_bridge_net_%s'  # project_id
ns_bridge_subnet_name = 'ns_bridge_subnet_%s'  # project_id
# for external gateway port: project_id b_router_id None
# for floating ip port: project_id None b_internal_port_id
ns_bridge_port_name = 'ns_bridge_port_%s_%s_%s'

MAX_INT = 0x7FFFFFFF
