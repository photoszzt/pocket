#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ $# -ne 1 ]; then
  echo "need to enter key file name used to access controller and bastion"
  exit 1
fi

keyFile=$1

cd $SCRIPT_DIR/create_controller
CONTROLLER_OUT=$(pulumi stack output -j)
CONTROLLER_IP=$(echo $CONTROLLER_OUT | jq -r .pocketControllerPrivateIP)
CONTROLLER_DNS=$(echo $CONTROLLER_OUT | jq -r .controllerPublicDNS)
cd -

cd $SCRIPT_DIR/create_vpc
VPC_OUT=$(pulumi stack output -j)
pocketVpcId=$(echo $VPC_OUT | jq -r .POCKET_VPC_ID)
publicSubnetId=$(echo $VPC_OUT | jq -r .publicSubnetId)

pocketVPCNetworkCidr=$(echo $VPC_OUT | jq -r .pocketVPCNetworkCidr)
publicSubnetCidr=$(echo $VPC_OUT | jq -r .publicSubnetCidr)
publicSubnetAz=$(echo $VPC_OUT | jq -r .publicSubnetAz)
cd -

echo "export NAME=\"pocketcluster.k8s.local\"" > $SCRIPT_DIR/env.sh
echo "export KOPS_STATE_STORE=\"s3://zzt-videos\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_ID=\"${pocketVpcId}\"" >> $SCRIPT_DIR/env.sh

echo "export POCKET_VPC_PUBLIC_SUBNET_ID=\"${publicSubnetId}\"" >> $SCRIPT_DIR/env.sh

echo "export POCKET_VPC_NETWORK_CIDR=\"${pocketVPCNetworkCidr}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_VPC_PUBLIC_NETWORK_CIDR=\"${publicSubnetCidr}\"" >> $SCRIPT_DIR/env.sh
echo "export POCKET_AWS_ZONE=\"${publicSubnetAz}\"" >> $SCRIPT_DIR/env.sh
chmod +x $SCRIPT_DIR/env.sh

echo "{" > $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"NAME\": \"pocketcluster.k8s.local\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"KOPS_STATE_STORE\": \"s3://zzt-videos\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_ID\": \"${pocketVpcId}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_SUBNET_ID\": \"${publicSubnetId}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_NETWORK_CIDR\": \"${pocketVPCNetworkCidr}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_VPC_PUBLIC_NETWORK_CIDR\": \"${publicSubnetCidr}\"," >> $SCRIPT_DIR/pocket-k8s-config.json
echo "  \"POCKET_AWS_ZONE\": \"${publicSubnetAz}\"" >> $SCRIPT_DIR/pocket-k8s-config.json
echo "}" >> $SCRIPT_DIR/pocket-k8s-config.json

scp -i $keyFile $SCRIPT_DIR/env.sh ubuntu@$CONTROLLER_DNS:~
scp -i $keyFile  $SCRIPT_DIR/pocket-k8s-config.json \
  ubuntu@$CONTROLLER_DNS:~
# also setup the credential
ssh -i $keyFile ubuntu@$CONTROLLER_DNS "mkdir -p ~/.aws && source \
  /home/ubuntu/k8s/bin/activate && ~/k8s/bin/aws configure set region us-east-1"
scp -i $keyFile $HOME/.aws/credentials \
  ubuntu@$CONTROLLER_DNS:~/.aws/
