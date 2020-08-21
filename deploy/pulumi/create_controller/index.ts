import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
// org is the organization name you use to create the stack
const org = config.require('org')
// keyName for the ec2 instance to use
const keyName = config.require('keyName')

const stack = pulumi.getStack()
const vpc = new pulumi.StackReference(`${org}/create_vpc/${stack}`);

const publicSubnetAz = vpc.getOutput("subnetPublicAz");
const publicSubnetId = vpc.getOutput("publicSubnetId");
const publicSubnetCidr = vpc.getOutput("subnetPublicCidr");

const privateSubnetAz = vpc.getOutput("subnetPrivateAz");
const privateSubnetId = vpc.getOutput("privateSubnetId");
const privateSubnetCidr = vpc.getOutput("subnetPrivateCidr");

const pocketVpcId = vpc.getOutput("POCKET_VPC_ID");

export const pocketControllerPrivateIP = "10.1.47.178";
const bastionSgId = vpc.getOutput("bastionSgId")

let userData =
`#!/bin/bash
sudo yum install -y git wget curl
wget -O kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x ./kops
sudo mv ./kops /usr/local/bin/

wget -O kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
sudo yum install -y python3
cd ~
python3 -m venv k8s
source activate k8s/bin/activate
python3 -m pip install -U pip setuptools
python3 -m pip install kubernetes
python3 -m pip install awscli

git clone https://github.com/photoszzt/pocket.git

echo "export NAME=pocketcluster.k8s.local" > ~/env.sh
echo "export KOPS_STATE_STORE=s3://zzt-videos" >> ~/env.sh
echo "export POCKET_VPC_ID=${pocketVpcId}" >> ~/env.sh

echo "export POCKET_VPC_PRIVATE_SUBNET_ID=${privateSubnetId}" >> ~/env.sh
echo "export POCKET_VPC_PUBLIC_SUBNET_ID=${publicSubnetId}" >> ~/env.sh

echo "export POCKET_VPC_NETWORK_CIDR=${pocketVpcId}" >> ~/env.sh
echo "export POCKET_VPC_PRIVATE_NETWORK_CIDR=${privateSubnetCidr}" >> ~/env.sh
echo "export POCKET_VPC_PUBLIC_NETWORK_CIDR=${publicSubnetCidr}" >> ~/env.sh

echo "export POCKET_AWS_ZONE=${privateSubnetAz}" >> ~/env.sh`

const pocket_controller = new aws.ec2.Instance("pocket-controller", {
    ami: "ami-02354e95b39ca8dec",
    instanceType: "c5.2xlarge",
    tags: {
        Name: "PocketController",
    },
    availabilityZone: privateSubnetAz,
    privateIp: pocketControllerPrivateIP,
    subnetId: privateSubnetId,
    keyName: keyName,
    vpcSecurityGroupIds: [bastionSgId],
    userData: userData
});

export const instanceId = pocket_controller.id;
