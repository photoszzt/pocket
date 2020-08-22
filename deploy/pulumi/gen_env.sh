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
privateSubnetId=$(echo $VPC_OUT | jq -r .privateSubnetId)
publicSubnetId=$(echo $VPC_OUT | jq -r .publicSubnetId)

pocketVPCNetworkCidr=$(echo $VPC_OUT | jq -r .pocketVPCNetworkCidr)
privateSubnetCidr=$(echo $VPC_OUT | jq -r .privateSubnetCidr)
publicSubnetCidr=$(echo $VPC_OUT | jq -r .publicSubnetCidr)
privateSubnetAz=$(echo $VPC_OUT | jq -r .privateSubnetAz)
vpcNatGatewayId=$(echo $VPC_OUT | jq -r .vpcNatGatewayId)
cd -

echo "export NAME=\"pocketcluster.k8s.local\"" > $SCRIPT_DIR/env.sh
echo "export KOPS_STATE_STORE=\"s3://zzt-videos\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_ID=\"${pocketVpcId}\"" >> $SCRIPT_DIR/env.sh

echo "export POCKET_VPC_PRIVATE_SUBNET_ID=\"${privateSubnetId}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_SUBNET_ID=\"${publicSubnetId}\"" >> $SCRIPT_DIR/env.sh

echo "export POCKET_VPC_NETWORK_CIDR=\"${pocketVPCNetworkCidr}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PRIVATE_NETWORK_CIDR=\"${privateSubnetCidr}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_NETWORK_CIDR=\"${publicSubnetCidr}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_AWS_ZONE=\"${privateSubnetAz}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_NAT_ID=\"${vpcNatGatewayId}\""  >> $SCRIPT_DIR/env.sh
chmod +x $SCRIPT_DIR/env.sh

echo "{" > $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"NAME\": \"pocketcluster.k8s.local\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"KOPS_STATE_STORE\": \"s3://zzt-videos\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_ID\": \"${pocketVpcId}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PRIVATE_SUBNET_ID\": \"${privateSubnetId}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_SUBNET_ID\": \"${publicSubnetId}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_NETWORK_CIDR\": \"${pocketVPCNetworkCidr}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PRIVATE_NETWORK_CIDR\": \"${privateSubnetCidr}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_NETWORK_CIDR\": \"${publicSubnetCidr}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_AWS_ZONE\": \"${privateSubnetAz}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_NAT_ID\": \"${vpcNatGatewayId}\""  >> $SCRIPT_DIR/pocket-k8s-config.json
echo "}" >> $SCRIPT_DIR/pocket-k8s-config.json

PROXY="ssh -W %h:%p -i $keyFile ubuntu@$BASTIONIP"
scp -i $keyFile -o ProxyCommand="$PROXY" $SCRIPT_DIR/env.sh \
  ubuntu@$CONTROLLER_IP:~
scp -i $keyFile -o ProxyCommand="$PROXY" $SCRIPT_DIR/pocket-k8s-config.json \
  ubuntu@$CONTROLLER_IP:~
# also setup the credential
ssh -i $keyFile -o ProxyCommand="$PROXY" ubuntu@$CONTROLLER_IP "mkdir -p ~/.aws && source \
  ~/k8s/bin/activate && aws configure set region us-east-1"
scp -i $keyFile -o ProxyCommand="$PROXY" $HOME/.aws/credentials \
  ubuntu@$CONTROLLER_IP:~/.aws/
