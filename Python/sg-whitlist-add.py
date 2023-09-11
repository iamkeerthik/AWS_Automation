import boto3

# Specify the IP address to whitelist
ip_address = '122.168.44.192/32'

# Specify the AWS profile name
aws_profile = 'prod'

# Specify the security groups with their specific regions
security_groups = [
    # {
    #     'region': 'ap-south-1',
    #     'security_group_id': 'sg-05a1ac5d5429db83e'
    # },
    # {
    #     'region': 'ap-south-1',
    #     'security_group_id': 'sg-0542e1389354d649b'
    # },
    {
        'region': 'eu-west-1',
        'security_group_id': 'sg-0e0a330d56662e6f5'
    },
    {
        'region': 'eu-west-1',
        'security_group_id': 'sg-00e060e0052296557'
    }
    #  {
    #     'region': 'us-east-1',
    #     'security_group_id': 'sg-0e28d8004012175fe'
    # },
    # {
    #     'region': 'us-east-1',
    #     'security_group_id': 'sg-06297e7beaf4c5c09'
    # },
    #  {
    #     'region': 'us-east-1',
    #     'security_group_id': 'sg-0fd826b238239ef5e'
    # },
    #  {
    #     'region': 'us-east-1',
    #     'security_group_id': 'sg-01d35315ca1af3ce6'
    # }

]

def whitelist_ip_address(ip, region, sg_id):
    try:
        session = boto3.Session(profile_name=aws_profile, region_name=region)
        ec2_client = session.client('ec2')
        response = ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [
                        {
                            'CidrIp': ip,
                            'Description': 'gauri-tbr'
                        },
                    ],
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [
                        {
                            'CidrIp': ip,
                            'Description': 'gauri-tbr'
                        },
                    ],
                },
            ],
        )
        print(f"Whitelisted IP {ip} in Security Group {sg_id} in region {region}")
    except Exception as e:
        print(f"Error whitelisting IP {ip} in Security Group {sg_id} in region {region}: {str(e)}")

# Whitelist IP in each security group within its specific region
for security_group in security_groups:
    region = security_group['region']
    sg_id = security_group['security_group_id']
    whitelist_ip_address(ip_address, region, sg_id)
