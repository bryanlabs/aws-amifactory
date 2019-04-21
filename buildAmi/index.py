import os
import boto3
import json
from botocore.exceptions import ClientError

# Ensure OS env variables are in place.
try:  
    S3Output = os.environ.get("S3OUTPUT")
    Prefix = os.environ.get("PREFIX")
    RotateAMIFunction = os.environ.get("ROTATEAMIFUNCTION")
    DestsubnetId = os.environ.get("DESTSUBNETID")
    IamInstanceProfileName = os.environ.get("IAMINSTANCEPROFILENAME")
    AutomationAssumeRole = os.environ.get("AUTOMATIONASSUMEROLE")
    KeyName = os.environ.get("KEYNAME")
    InstanceType = os.environ.get("INSTANCETYPE")
    SecurityGroupId = os.environ.get("SECURITYGROUPID")
    DefaultLinuxAmiDocument = os.environ.get("DEFAULTLINUXAMIDOCUMENT")
    DefaultWindowsAmiDocument = os.environ.get("DEFAULTWINDOWSAMIDOCUMENT")
    AuthorizedKey = os.environ.get("AUTHORIZEDKEY")
except KeyError: 
    print("Not exist environment value for %s" % "key_maybe_not_exist")

# Lambda Handler
def lambda_handler(event, context):

    try:
        # Execute the SSM Automation for each AMI defined.
        client = boto3.client('ssm')
        for ami in event['amis']:
            accounts = ','.join(ami['accounts'])
            if ami['automationDocument'] == 'DefaultLinuxAmiDocument':
                Document = DefaultLinuxAmiDocument
            elif ami['automationDocument'] == 'DefaultWindowsAmiDocument':
                Document = DefaultWindowsAmiDocument
            else:
                Document = ami['automationDocument']

            client.start_automation_execution(
                DocumentName=Document,
                Parameters={
                    'S3Output': [ S3Output ],
                    'Prefix': [ Prefix ],
                    'RotateAMIFunction': [ RotateAMIFunction ],
                    'DestSubnetId': [ DestsubnetId ],
                    'IamInstanceProfileName': [ IamInstanceProfileName ],
                    'AutomationAssumeRole': [ AutomationAssumeRole ],
                    'KeyName': [ KeyName ],
                    'InstanceType': [ 't2.medium' ],
                    'SecurityGroupId' : [ SecurityGroupId ],
                    'AmiType': [ ami['imageName'] ],
                    'SourceAmiId': [ ami['sourceImage'] ],
                    'Accounts': [ accounts ],
                    'PreUpdateScript': [ ami['bootstrapUrl'] ],
                    'AuthorizedKey': [ AuthorizedKey ]
                }
            )
            print(f"Started Automation for: {ami['name']}, using document {Document}")
    # Handle errors
    except ClientError as e:
        print("Unexpected error: %s" % e)
