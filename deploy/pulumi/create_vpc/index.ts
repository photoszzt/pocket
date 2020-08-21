import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

const vpc_name = "pocket-aws";
export const pocketVPCNetworkCidr = "10.1.0.0/16";
export const subnetPublicName = "pocket-kube-public"
export const subnetPrivateName = "pocket-kube-private"
export const subnetPublicCidr = "10.1.129.32/27"
export const subnetPrivateCidr = "10.1.0.0/17"
export const subnetPublicAz="us-east-1c"
export const subnetPrivateAz="us-east-1c"
const vpc = new awsx.ec2.Vpc(vpc_name, {
    cidrBlock: pocketVPCNetworkCidr,
    subnets: [
        {
            type: "public",
            name: subnetPublicName,
            location: {
                availabilityZone: subnetPublicAz,
                cidrBlock: subnetPublicCidr,
            },
        },
        {
            type: "private",
            name: subnetPrivateName,
            location: {
                availabilityZone: subnetPrivateAz,
                cidrBlock: subnetPrivateCidr,
            },
        }
    ],
    numberOfNatGateways: 1,
    numberOfAvailabilityZones: 1,
});

const bastionSg = new awsx.ec2.SecurityGroup('pocket-aws-bastion', { vpc });
bastionSg.createIngressRule("ssh-access", {
    location: { cidrBlocks: [ "0.0.0.0/0" ]},
    ports: { protocol: "tcp", fromPort: 22 },
    description: "allow ssh access"
});
bastionSg.createEgressRule("outbound-access", {
    location: { cidrBlocks: [ "0.0.0.0/0" ] },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow outbound access to anywhere",
});

export const POCKET_VPC_ID = vpc.id;
export const vpcPrivateSubnets = vpc.privateSubnets;
export const vpcPublicSubnets = vpc.publicSubnets;
export const privateSubnetId = vpcPrivateSubnets.then(
    privateSubnets => privateSubnets[0]["subnet"]["id"]);
export const publicSubnetId = vpcPublicSubnets.then(
    publicSubnets => publicSubnets[0]["subnet"]["id"]
);
export const bastionSgId = bastionSg.id;
