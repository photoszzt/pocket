#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

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
