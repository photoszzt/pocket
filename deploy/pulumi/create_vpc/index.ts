import * as awsx from "@pulumi/awsx";

const vpc_name = "pocket-aws";
export const pocketVPCNetworkCidr = "10.1.0.0/16";
export const publicSubnetName = "pocket-kube-public"
export const privateSubnetName = "pocket-kube-private"
export const publicSubnetCidr = "10.1.129.32/27"
export const privateSubnetCidr = "10.1.0.0/17"
export const publicSubnetAz="us-east-1c"
export const privateSubnetAz="us-east-1c"
const vpc = new awsx.ec2.Vpc(vpc_name, {
    cidrBlock: pocketVPCNetworkCidr,
    subnets: [
        {
            type: "public",
            name: publicSubnetName,
            location: {
                availabilityZone: publicSubnetAz,
                cidrBlock: publicSubnetCidr,
            },
        },
        {
            type: "private",
            name: privateSubnetName,
            location: {
                availabilityZone: privateSubnetAz,
                cidrBlock: privateSubnetCidr,
            },
        }
    ],
    numberOfNatGateways: 1,
    numberOfAvailabilityZones: 1,
});
let defaultSgId = vpc.vpc.defaultSecurityGroupId
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

const vmSg = new awsx.ec2.SecurityGroup('vm', { vpc });
vmSg.createIngressRule("vmSsh-access", {
    location: { cidrBlocks: [ "0.0.0.0/0" ]},
    ports: { protocol: "tcp", fromPort: 22 },
    description: "allow ssh access"
});
vmSg.createIngressRule("vmInternal-access", {
    location: { sourceSecurityGroupId: defaultSgId },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow all internal inbound access"
})
vmSg.createEgressRule("vmOutbound-access", {
    location: { cidrBlocks: [ "0.0.0.0/0" ] },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow outbound access to anywhere",
});

export const POCKET_VPC_ID = vpc.id;
const vpcPrivateSubnets = vpc.privateSubnets;
const vpcPublicSubnets = vpc.publicSubnets;
export const vpcNatGatewayId = vpc.natGateways.then(
    natGateways => natGateways[0]["natGateway"]["id"]
);
export const privateSubnetId = vpcPrivateSubnets.then(
    privateSubnets => privateSubnets[0]["subnet"]["id"]);
export const publicSubnetId = vpcPublicSubnets.then(
    publicSubnets => publicSubnets[0]["subnet"]["id"]
);
export const bastionSgId = bastionSg.id;
export const vmSgId = vmSg.id;
