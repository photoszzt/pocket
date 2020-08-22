import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
// org is the organization name you use to create the stack
const org = config.require('org')
// keyName for the ec2 instance to use
const keyName = config.require('keyName')

const stack = pulumi.getStack()
const vpc = new pulumi.StackReference(`${org}/create_vpc/${stack}`);

const privateSubnetAz = vpc.getOutput("privateSubnetAz");
const privateSubnetId = vpc.getOutput("privateSubnetId");

export const pocketControllerPrivateIP = "10.1.47.178";
const vmSgId = vpc.getOutput("vmSgId")

let userData =
`#!/bin/bash
sudo apt update
sudo apt install -y git wget curl tmux python3-venv jq
wget -O kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x ./kops
sudo mv ./kops /usr/local/bin/

wget -O kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

cd /home/ubuntu
git clone https://github.com/photoszzt/pocket.git
sudo chown -R ubuntu:ubuntu pocket

sudo apt install -y python3
python3 -m venv k8s
sudo chown -R ubuntu:ubuntu k8s
source k8s/bin/activate
python3 -m pip install -U pip setuptools wheel
python3 -m pip install kubernetes awscli pandas`

const pocket_controller = new aws.ec2.Instance("pocket-controller", {
    ami: "ami-0bcc094591f354be2",
    instanceType: "c5.2xlarge",
    tags: {
        Name: "PocketController",
    },
    availabilityZone: privateSubnetAz,
    privateIp: pocketControllerPrivateIP,
    subnetId: privateSubnetId,
    keyName: keyName,
    vpcSecurityGroupIds: [vmSgId],
    userData: userData
});

export const instanceId = pocket_controller.id;
