#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ $# -ne 1 ]; then
  echo "need to enter key file name used to access controller and bastion"
  exit 1
fi

keyFile=$1

cd $SCRIPT_DIR/create_bastion
BASTION_OUT=$(pulumi stack output -j)
BASTIONIP=$(echo $BASTION_OUT | jq -r .bastionIP)
cd -
cd $SCRIPT_DIR/create_controller
CONTROLLER_OUT=$(pulumi stack output -j)
CONTROLLER_IP=$(echo $CONTROLLER_OUT | jq -r .pocketControllerPrivateIP)
cd -

cd $SCRIPT_DIR/create_vpc
VPC_OUT=$(pulumi stack output -j)
pocketVpcId=$(echo $VPC_OUT | jq -r .POCKET_VPC_ID)
privateSubnetId1=$(echo $VPC_OUT | jq -r .privateSubnetId1)
privateSubnetId2=$(echo $VPC_OUT | jq -r .privateSubnetId2)
publicSubnetId1=$(echo $VPC_OUT | jq -r .publicSubnetId1)
publicSubnetId2=$(echo $VPC_OUT | jq -r .publicSubnetId2)

pocketVPCNetworkCidr=$(echo $VPC_OUT | jq -r .pocketVPCNetworkCidr)
privateSubnetCidr1=$(echo $VPC_OUT | jq -r .privateSubnetCidr1)
privateSubnetCidr2=$(echo $VPC_OUT | jq -r .privateSubnetCidr2)
publicSubnetCidr1=$(echo $VPC_OUT | jq -r .publicSubnetCidr1)
publicSubnetCidr2=$(echo $VPC_OUT | jq -r .publicSubnetCidr2)
privateSubnetAz1=$(echo $VPC_OUT | jq -r .privateSubnetAz1)
privateSubnetAz2=$(echo $VPC_OUT | jq -r .privateSubnetAz2)
vpcNatGatewayId=$(echo $VPC_OUT | jq -r .vpcNatGatewayId)
cd -

echo "export NAME=\"pocketcluster.k8s.local\"" > $SCRIPT_DIR/env.sh
echo "export KOPS_STATE_STORE=\"s3://zzt-videos\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_ID=\"${pocketVpcId}\"" >> $SCRIPT_DIR/env.sh

echo "export POCKET_VPC_PRIVATE_SUBNET_ID1=\"${privateSubnetId1}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PRIVATE_SUBNET_ID2=\"${privateSubnetId2}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_SUBNET_ID1=\"${publicSubnetId1}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_SUBNET_ID2=\"${publicSubnetId2}\"" >> $SCRIPT_DIR/env.sh

echo "export POCKET_VPC_NETWORK_CIDR=\"${pocketVPCNetworkCidr}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PRIVATE_NETWORK_CIDR1=\"${privateSubnetCidr1}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PRIVATE_NETWORK_CIDR2=\"${privateSubnetCidr2}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_NETWORK_CIDR1=\"${publicSubnetCidr1}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_NETWORK_CIDR2=\"${publicSubnetCidr2}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_AWS_ZONE1=\"${privateSubnetAz1}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_AWS_ZONE2=\"${privateSubnetAz2}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_NAT_ID=\"${vpcNatGatewayId}\""  >> $SCRIPT_DIR/env.sh
echo "export BASTIONIP=\"${BASTIONIP}\"" >>  $SCRIPT_DIR/env.sh
chmod +x $SCRIPT_DIR/env.sh

echo "{" > $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"NAME\": \"pocketcluster.k8s.local\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"KOPS_STATE_STORE\": \"s3://zzt-videos\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_ID\": \"${pocketVpcId}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PRIVATE_SUBNET_ID1\": \"${privateSubnetId1}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PRIVATE_SUBNET_ID2\": \"${privateSubnetId2}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_SUBNET_ID1\": \"${publicSubnetId1}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_SUBNET_ID2\": \"${publicSubnetId2}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_NETWORK_CIDR\": \"${pocketVPCNetworkCidr}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PRIVATE_NETWORK_CIDR1\": \"${privateSubnetCidr1}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PRIVATE_NETWORK_CIDR2\": \"${privateSubnetCidr2}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_NETWORK_CIDR1\": \"${publicSubnetCidr1}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_NETWORK_CIDR2\": \"${publicSubnetCidr2}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_AWS_ZONE1\": \"${privateSubnetAz1}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_AWS_ZONE2\": \"${privateSubnetAz2}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_NAT_ID\": \"${vpcNatGatewayId}\","  >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"BASTIONIP\": \"${BASTIONIP}\"" >> $SCRIPT_DIR/pocket-k8s-config.json
echo "}" >> $SCRIPT_DIR/pocket-k8s-config.json

PROXY="ssh -W %h:%p -i $keyFile ubuntu@$BASTIONIP"
scp -i $keyFile -o ProxyCommand="$PROXY" $SCRIPT_DIR/env.sh \
  ubuntu@$CONTROLLER_IP:~
scp -i $keyFile -o ProxyCommand="$PROXY" $SCRIPT_DIR/pocket-k8s-config.json \
  ubuntu@$CONTROLLER_IP:~
# also setup the credential
ssh -i $keyFile -o ProxyCommand="$PROXY" ubuntu@$CONTROLLER_IP "mkdir -p ~/.aws && source \
  /home/ubuntu/k8s/bin/activate && ~/k8s/bin/aws configure set region us-east-1"
scp -i $keyFile -o ProxyCommand="$PROXY" $HOME/.aws/credentials \
  ubuntu@$CONTROLLER_IP:~/.aws/
