import boto3
import pandas as pd

# Enter the list of regions to scan
regions = ['ap-south-1', 'us-east-2']

# Enter the profile name to use for authentication
profile_name = 'Stage'

# Initialize an empty list to store the results
results = []

# Iterate through all regions and retrieve security group rules
for region in regions:
    # Initialize Boto3 session with the specified profile and region
    session = boto3.Session(profile_name=profile_name, region_name=region)

    # Initialize Boto3 client for EC2 service using the session
    ec2 = session.client('ec2')

    # Retrieve all security groups in the region
    security_groups = ec2.describe_security_groups()['SecurityGroups']

    # Add a region heading to the results list
    results.append({'Region': region})

    # Iterate through all security groups and their inbound rules
    for sg in security_groups:
        for rule in sg['IpPermissions']:
            # Check if the source IP address is 0.0.0.0/0
            if 'IpRanges' in rule and any([ip_range['CidrIp'] == '0.0.0.0/0' for ip_range in rule['IpRanges']]):
                # If the source IP address is 0.0.0.0/0, add the security group details to the results list
                result = {
                    'Group Name': sg['GroupName'],
                    'Group ID': sg['GroupId'],
                    'Protocol': rule['IpProtocol'],
                    'Port Range': f"{rule['FromPort']}-{rule['ToPort']}",
                    'Source': '0.0.0.0/0'
                }
                results.append(result)

    # Add a one-row gap between regions in the results list
    results.append({})

# Convert the results list to a pandas DataFrame and write it to an Excel file
df = pd.DataFrame(results)
df.to_excel('sg_rules(0.0.0.0).xlsx', index=False)
