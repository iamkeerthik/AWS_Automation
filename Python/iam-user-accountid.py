import boto3

def get_username_and_account_id(access_key, secret_key):
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    sts_client = session.client('sts')

    try:
        response = sts_client.get_caller_identity()
        user_arn = response['Arn']
        account_id = user_arn.split(':')[4]
        username = user_arn.split('/')[-1]
        return username, account_id
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

# Replace 'YOUR_ACCESS_KEY' and 'YOUR_SECRET_KEY' with the AWS access and secret keys you want to check
access_key = 'YOUR_ACCESS_KEY'
secret_key = 'YOUR_SECRET_KEY'

username, account_id = get_username_and_account_id(access_key, secret_key)
if username and account_id:
    print(f"IAM User Name: {username}")
    print(f"AWS Account ID: {account_id}")
else:
    print("Failed to retrieve the IAM user name and AWS account ID.")
