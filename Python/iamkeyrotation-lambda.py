import boto3
from datetime import datetime, timedelta, timezone

def lambda_handler(event, context):
    try:
        # IAM client
        iam_client = boto3.client('iam')
        # SES client
        ses_client = boto3.client('ses')

        # Get all IAM users in the account
        response = iam_client.list_users()
        users = response['Users']

        # List to store users whose access keys have been rotated
        rotated_users = []

        # Iterate over each IAM user
        for user in users:
            username = user['UserName']
            email_address = username  # Use username as email address by default

            # Check if the IAM user's email address is verified in SES
            email_verified = is_email_verified(ses_client, email_address)

            # If email is not verified, set a default recipient email address
            if not email_verified:
                email_address = 'Keerthik.shenoy@42gears.com'

            # List the access keys for the IAM user
            response = iam_client.list_access_keys(UserName=username)
            access_keys = response['AccessKeyMetadata']

            # Iterate over each access key
            for access_key in access_keys:
                access_key_id = access_key['AccessKeyId']
                access_key_create_date = access_key['CreateDate']

                # Convert access_key_create_date to offset-aware datetime
                access_key_create_date = access_key_create_date.replace(tzinfo=timezone.utc)

                # Calculate the age of the access key in days
                key_age = (datetime.now(timezone.utc) - access_key_create_date).days

                # Check if the access key age is greater than 90 days
                if key_age > 90:
                    # Delete the access key
                    iam_client.delete_access_key(UserName=username, AccessKeyId=access_key_id)

                    # Create a new access key
                    response = iam_client.create_access_key(UserName=username)
                    new_access_key_id = response['AccessKey']['AccessKeyId']
                    new_secret_access_key = response['AccessKey']['SecretAccessKey']

                    # Add the username to the rotated_users list
                    rotated_users.append(username)

                    # Print the access key details
                    print(f"Access Key Rotated for User: {username}")
                    print(f"Old Access Key ID: {access_key_id}")
                    print(f"New Access Key ID: {new_access_key_id}")
                    print(f"Secret Access Key: {new_secret_access_key}")
                    print("--------------------")

                    # Send email with the new access key details to the user's email address
                    send_email(ses_client, email_address, new_access_key_id, new_secret_access_key)

            # Print message if no key rotation occurred for the user
            if not access_keys:
                print(f"No IAM user access key rotation needed for user: {username}")

        # Send an email with the list of rotated users
        if rotated_users:
            send_rotation_summary_email(ses_client, rotated_users)

        # Print message if no user key rotation occurred
        if not rotated_users:
            print("No IAM user access key rotation needed for any user.")

        return {
            'statusCode': 200,
            'body': 'IAM access key rotation completed successfully.'
        }
    except Exception as e:
        # Handle the exception and return an error response
        error_message = f"Error: {str(e)}"
        print(error_message)
        return {
            'statusCode': 500,
            'body': error_message
        }


def is_email_verified(ses_client, email_address):
    response = ses_client.list_identities(IdentityType='EmailAddress')
    verified_email_addresses = response['Identities']

    return email_address in verified_email_addresses


def send_email(ses_client, recipient_email, access_key_id, secret_access_key):
    sender_email = 'your-sender-email@example.com'

    subject = f"New Access Key for User: {recipient_email}"
    message = f"Hello {recipient_email},\n\nA new access key has been created for your AWS IAM user.\n\n" \
              f"Access Key ID: {access_key_id}\n" \
              f"Secret Access Key: {secret_access_key}\n\n" \
              f"Please make sure to securely store and update your credentials.\n\n"

    response = ses_client.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': message}}
        }
    )

    return response


def send_rotation_summary_email(ses_client, rotated_users):
    sender_email = 'Keerthik.shenoy@42gears.com'

    subject = "IAM Access Key Rotation Summary"
    message = f"The following IAM users' access keys have been rotated:\n\n"

    for username in rotated_users:
        message += f"- {username}\n"

    # If no users' keys were rotated, print a message
    if not rotated_users:
        message = "No IAM user access key rotation needed for any user."

    response = ses_client.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [sender_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': message}}
        }
    )

    return response