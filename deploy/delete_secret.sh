#!/bin/bash
set -euo pipefail

ID=$1
kops delete secret --name pocketcluster.k8s.local --state s3://zzt-videos sshpublickey admin $ID
