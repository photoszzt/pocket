import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
// org is the organization name you use to create the stack
const org = config.require('org')
// keyName for the ec2 instance to use
const keyName = config.require('keyName')

const stack = pulumi.getStack()
const vpc = new pulumi.StackReference(`${org}/create_vpc/${stack}`);
const privateSubnetAvailabilityZone = vpc.getOutput("subnetPrivateAz");
const privateSubnetId = vpc.getOutput("privateSubnetId")
const pocketControllerPrivateIP = "10.1.47.178";
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
pip install -U pip setuptools
pip install kubernetes
pip install awscli`

const pocket_controller = new aws.ec2.Instance("pocket-controller", {
    ami: "ami-02354e95b39ca8dec",
    instanceType: "c5.2xlarge",
    tags: {
        Name: "PocketController",
    },
    availabilityZone: privateSubnetAvailabilityZone,
    privateIp: pocketControllerPrivateIP,
    subnetId: privateSubnetId,
    associatePublicIpAddress: true,
    keyName: keyName,
    vpcSecurityGroupIds: [bastionSgId],
    userData: userData
});

export const instanceId = pocket_controller.id;
