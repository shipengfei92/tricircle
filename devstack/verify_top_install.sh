#!/bin/bash
#
# This script is to verify the installation of Tricircle
#
# Execute this script in the top OpenStack
#
# Author: Pengfei Shi <shipengfei92@gmail.com>
#

TEST_DIR=$(pwd)
echo "Test work directy is $TEST_DIR."

echo "Source client environment:"
source $TEST_DIR/admin-openrc.sh

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

echo "******************************"
echo "*         Verify Nova        *"
echo "******************************"

echo "Show nova aggregate:"
nova --debug aggregate-list

echo "Create test flavor:"
nova --debug flavor-create test 1 1024 10 1

echo "******************************"
echo "*       Verify Neutron       *"
echo "******************************"

echo "Create net1:"
neutron --debug net-create --availability-zone=az1 net1

echo "Create subnet of net1:"
neutron --debug subnet-create net1 10.0.0.0/24

image_id=$(glance image-list |awk 'NR==4 {print $2}')
net_id=$(neutron net-list|grep net1 |awk '{print $2}')

echo "Boot vm1 in az1:"
nova --debug boot --flavor 1 --image $image_id --nic net-id=$net_id --availability-zone az1 vm1

echo "******************************"
echo "*        Verify Cinder       *"
echo "******************************"

echo "Create a volume in az1:"
cinder --debug create --availability-zone=az1 1

echo "Show volume list:"
cinder --debug list
volume_id=$(cinder list |grep lvmdriver-1 | awk '{print $2}')

echo "Show detailed volume info:"
cinder --debug show $volume_id

echo "Delete test volume:"
cinder --debug delete $volume_id
cinder --debug list
