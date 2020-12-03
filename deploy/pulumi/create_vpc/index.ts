import * as awsx from "@pulumi/awsx";
import * as aws from "@pulumi/aws";

const vpc_name = "pocket-aws";
const region = "us-east-1"
export const pocketVPCNetworkCidr = "10.1.0.0/16";
export const publicSubnetName = "pocket-kube-public"
export const publicSubnetCidr = "10.1.0.0/17"
export const publicSubnetAz = "us-east-1d"
const vpc = new awsx.ec2.Vpc(vpc_name, {
    cidrBlock: pocketVPCNetworkCidr,
    subnets: [
        {
            type: "public",
            name: publicSubnetName + "1",
            location: {
                availabilityZone: publicSubnetAz,
                cidrBlock: publicSubnetCidr,
            },
        },
    ],
    numberOfNatGateways: 0,
    numberOfAvailabilityZones: 1,
});
let defaultSgId = vpc.vpc.defaultSecurityGroupId
// this security group is for vm and lambda; the name is chosen in the patch-cluster.py script
const pocketRelaxSg = new awsx.ec2.SecurityGroup('pocket-kube-relax', { vpc });
pocketRelaxSg.createIngressRule("relaxSsh-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "tcp", fromPort: 22 },
    description: "allow ssh access"
});
pocketRelaxSg.createIngressRule("pocketDefaultSg-access", {
    location: { sourceSecurityGroupId: defaultSgId },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow all internal inbound access"
})
pocketRelaxSg.createIngressRule("relaxSg-access", {
    location: { sourceSecurityGroupId: pocketRelaxSg.id },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow all internal inbound access"
})
pocketRelaxSg.createIngressRule("relaxSg-https-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "tcp", fromPort: 443 },
    description: "allow all internal inbound access"
})
pocketRelaxSg.createEgressRule("relax-outbound-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow outbound access to anywhere",
});

const bastionSg = new awsx.ec2.SecurityGroup('pocket-aws-bastion', { vpc });
bastionSg.createIngressRule("ssh-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "tcp", fromPort: 22 },
    description: "allow ssh access"
});
bastionSg.createEgressRule("outbound-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow outbound access to anywhere",
});

const vmSg = new awsx.ec2.SecurityGroup('vm', { vpc });
vmSg.createIngressRule("vmSsh-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "tcp", fromPort: 22 },
    description: "allow ssh access"
});
vmSg.createIngressRule("vmPocketDefaultSg-access", {
    location: { sourceSecurityGroupId: defaultSgId },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow all internal inbound access"
})
vmSg.createEgressRule("vmOutbound-access", {
    location: { cidrBlocks: ["0.0.0.0/0"] },
    ports: { protocol: "-1", fromPort: 0, toPort: 0 },
    description: "allow outbound access to anywhere",
});

const s3 = new aws.ec2.VpcEndpoint("s3", {
    vpcId: vpc.id,
    serviceName: "com.amazonaws." + region + ".s3",
});

export const POCKET_VPC_ID = vpc.id;
const vpcPublicSubnets = vpc.publicSubnets;
export const publicSubnetId = vpcPublicSubnets.then(
    publicSubnets => publicSubnets[0]["subnet"]["id"]
);
export const bastionSgId = bastionSg.id;
export const vmSgId = vmSg.id;
export const pocketRelaxSgId = pocketRelaxSg.id;
