import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
// org is the organization name you use to create the stack
const org = config.require('org')
const keyName = config.require('keyName')
const stack = pulumi.getStack()
const vpc = new pulumi.StackReference(`${org}/create_vpc/${stack}`);
const publicSubnetAvailabilityZone = vpc.getOutput("publicSubnetAz");
const publicSubnetId = vpc.getOutput("publicSubnetId")
const bastionSgId = vpc.getOutput("bastionSgId")

const bastion = new aws.ec2.Instance("bastion", {
    ami: "ami-0bcc094591f354be2",
    instanceType: "t2.micro",
    tags: {
        Name: "pocket-bastion"
    },
    availabilityZone: publicSubnetAvailabilityZone,
    subnetId: publicSubnetId,
    keyName: keyName,
    vpcSecurityGroupIds: [bastionSgId]
});

export const bastionIP = bastion.publicDns
