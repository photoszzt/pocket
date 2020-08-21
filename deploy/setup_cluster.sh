#/bin/bash

set -euo pipefail
if [ $# -ne 1 ]; then
    echo "please provide config json file"
    exit 1
fi

CONFIG=$(cat $1)
CLUSTER_NAME="$(echo ${CONFIG} | jq -r .NAME)"

kops toolbox template --name ${CLUSTER_NAME} --values <( echo ${CONFIG}) --template pocketcluster.template.yaml --format-yaml > pocketcluster.k8s.local.yaml

kops replace -f pocketcluster.k8s.local.yaml --name ${CLUSTER_NAME} --force

kops create secret --name ${CLUSTER_NAME} sshpublickey admin -i ~/.ssh/id_rsa.pub

kops update cluster --name ${CLUSTER_NAME} --yes

#  Then wait. 
#  When cluster running (check with `kops validate cluster`), run the following commands:
#
# kops create instancegroup bastions --role Bastion --subnet utility-us-west-2c --name ${NAME}
# kops update cluster ${NAME} --yes
