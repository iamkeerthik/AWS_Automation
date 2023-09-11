import csv
import jmespath
import boto3
import os
import argparse

# Function to get EBS volume details for each volume ID
def get_volume_details(volume_ids, ec2_client):
    volumes_details = []
    for volume_id in volume_ids:
        volume_response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        volume_details = jmespath.search("Volumes[].[VolumeId, Size]", volume_response)
        if volume_details:
            volumes_details.append(volume_details[0])
    return volumes_details

def main():
    # Replace with the AWS region you want to list EC2 instances from
    region = 'eu-west-1'

    # Replace with the name of the AWS profile you want to use
    aws_profile = 'sharath-oldlive'

    # Get EC2 client for specified profile and region
    session = boto3.Session(profile_name=aws_profile, region_name=region)
    ec2_client = session.client('ec2')

    # Get list of EC2 instances and their EBS volumes
    response = ec2_client.describe_instances()
    output = jmespath.search("Reservations[].Instances[].[NetworkInterfaces[0].OwnerId, InstanceId, InstanceType, \
                State.Name, Placement.AvailabilityZone, PrivateIpAddress, PublicIpAddress, KeyName, [Tags[?Key=='Name'].Value] [0][0], \
                BlockDeviceMappings[*].Ebs.VolumeId, BlockDeviceMappings[*].DeviceName, VpcId, LaunchTime]", response)

    # Get EBS volume details for each volume ID
    for instance in output:
        volume_ids = instance[9]
        volume_details = get_volume_details(volume_ids, ec2_client)
        instance[9] = [vol[0] for vol in volume_details]  # Extracting Volume IDs
        instance.insert(10, [vol[1] for vol in volume_details])  # Inserting Volume Sizes
        del instance[11]  # Removing the old combined column

    # Write output to CSV file with headers
    with open(f"{aws_profile}-{region}-ec2-inventory.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['AccountID','InstanceID','Type','State','AZ','PrivateIP','PublicIP','KeyPair','Name','VolumeID','VolumeSize','VPC_Name', 'LaunchTime'])
        writer.writerows(output)

    print("EC2 inventory complete")

if __name__ == "__main__":
    main()
