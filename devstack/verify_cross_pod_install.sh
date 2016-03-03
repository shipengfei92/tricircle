#!/bin/bash
#
# This script is to verify the installation of Tricircle in cross pod L3 networking.
#
# Execute this script in the Node1
#
# Author: Pengfei Shi <shipengfei92@gmail.com>
#


TEST_DIR=$(pwd)
echo "Test work directy is $TEST_DIR."

echo "Source client environment:"
source $TEST_DIR/adminrc.sh

echo "******************************"
echo "*       Verify Endpoint      *"
echo "******************************"

echo "List openstack endpoint:"
openstack --debug endpoint list

token=$(openstack token issue | awk 'NR==5 {print $4}')

echo $token

curl -X POST http://127.0.0.1:19999/v1.0/pods -H "Content-Type: application/json" \
    -H "X-Auth-Token: $token" -d '{"pod": {"pod_name":  "RegionOne"}}'

curl -X POST http://127.0.0.1:19999/v1.0/pods -H "Content-Type: application/json" \
    -H "X-Auth-Token: $token" -d '{"pod": {"pod_name":  "Pod1", "az_name": "az1"}}'

curl -X POST http://127.0.0.1:19999/v1.0/pods -H "Content-Type: application/json" \
    -H "X-Auth-Token: $token" -d '{"pod": {"pod_name":  "Pod2", "az_name": "az2"}}'

echo "******************************"
echo "*         Verify Nova        *"
echo "******************************"

echo "Show nova aggregate:"
nova aggregate-list

curl -X POST http://127.0.0.1:9696/v2.0/networks -H "Content-Type: application/json" \
    -H "X-Auth-Token: $token" \
    -d '{"network": {"name": "net1", "admin_state_up": true, "availability_zone_hints": ["az1"]}}'
curl -X POST http://127.0.0.1:9696/v2.0/networks -H "Content-Type: application/json" \
    -H "X-Auth-Token: $token" \
    -d '{"network": {"name": "net2", "admin_state_up": true, "availability_zone_hints": ["az2"]}}'

echo "Create test flavor:"
nova flavor-create test 1 1024 10 1

echo "******************************"
echo "*       Verify Neutron       *"
echo "******************************"

echo "Create net1 in Node1:"
neutron subnet-create net1 10.0.1.0/24

echo "Create net2 in Node2:"
neutron subnet-create net2 10.0.2.0/24

net1_id=$(neutron net-list |grep net1 | awk '{print $2}')
net2_id=$(neutron net-list |grep net2 | awk '{print $2}')
image_id=$(glance image-list |awk 'NR==4 {print $2}')

echo "Boot vm1 in az1:"
nova boot --flavor 1 --image $image_id --nic net-id=$net1_id --availability-zone az1 vm1
echo "Boot vm2 in az2:"
nova boot --flavor 1 --image $image_id --nic net-id=$net2_id --availability-zone az2 vm2

subnet1_id=$(neutron net-list |grep net1 |awk '{print $6}')
subnet2_id=$(neutron net-list |grep net2 |awk '{print $6}')

echo "Create router for subnets:"
neutron router-create router

echo "Add interface of subnet1:"
neutron router-interface-add router $subnet1_id
echo "Add interface of subnet2:"
neutron router-interface-add router $subnet2_id

echo "******************************"
echo "*   Verify VNC connection    *"
echo "******************************"

echo "Get the VNC url of vm1:"
nova --os-region-name Pod1 get-vnc-console vm1 novnc
echo "Get the VNC url of vm2:"
nova --os-region-name Pod2 get-vnc-console vm2 novnc

