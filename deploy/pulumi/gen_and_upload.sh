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

$SCRIPT_DIR/gen_config.sh

scp -i $keyFile $SCRIPT_DIR/env.sh ubuntu@$CONTROLLER_DNS:~
scp -i $keyFile  $SCRIPT_DIR/pocket-k8s-config.json \
  ubuntu@$CONTROLLER_DNS:~
# also setup the credential
ssh -i $keyFile ubuntu@$CONTROLLER_DNS "mkdir -p ~/.aws && source \
  /home/ubuntu/k8s/bin/activate && ~/k8s/bin/aws configure set region us-east-1"
scp -i $keyFile $HOME/.aws/credentials \
  ubuntu@$CONTROLLER_DNS:~/.aws/
