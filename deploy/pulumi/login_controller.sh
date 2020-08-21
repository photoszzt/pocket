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

ssh -i $keyFile -o ProxyCommand="ssh -W %h:%p -i $keyFile ec2-user@$BASTIONIP" ec2-user@$CONTROLLER_IP
