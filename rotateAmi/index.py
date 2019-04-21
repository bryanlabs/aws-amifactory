import boto3
import botocore
from dateutil import parser
import json

client = boto3.client('ec2')

# Deletes Snapshots for Images.
def deleteSnapshot(images, exclude=None):
    for image in images:
        snapshot = image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
        if exclude == None or exclude != image:
            print(f"Deleted Snapshot: {snapshot} for superseded image: {image['ImageId']}")
            client.delete_snapshot(SnapshotId=snapshot)
        else:
            print(f"Kept Snapshot: {snapshot} for latest image: {image['ImageId']}")

# Deregisters all but the latest image in a list.
def deregisterAllButLatestImage(images):    
    latestImageDate, _ = findLatest(images)

    for image in images:
        imageid = image['ImageId']
        imageDate = getUtcDate(image['CreationDate'])
    
        if imageDate < latestImageDate:
            try:
                client.deregister_image(ImageId=imageid)
                print(f"Deregistered image: {imageid}")
            except botocore.exceptions.ClientError as ex:
                print(f"Exception calling deregister_image: {str(ex)}")
        else:
            print(f"Kept Latest image: {imageid} from: {str(imageDate)}")

# Describe Images based on a filter.
def describeImagesWithFilter(imagePrefix):
    response = client.describe_images(
        Filters=[
            { 
                'Name': 'name',
                'Values': [imagePrefix + '*',]
            },
        ],
        Owners=['self',]
    )
    images = response['Images']
    return images

# Finds the latest Image in a list.
def findLatest(images):
    latestImageDate = None
    latestImage = None
    
    for image in images:
        currentAmiDate = getUtcDate(image['CreationDate'])

        if latestImageDate == None:
            latestImageDate = currentAmiDate
            latestImage = image
        elif currentAmiDate > latestImageDate:
            latestImageDate = currentAmiDate
            latestImage = image
    
    return latestImageDate, latestImage

# Converts a String to a UTC formated Date.    
def getUtcDate(strDate):
    return parser.parse(strDate)            
    
# Lambda Handler
def lambda_handler(event, context):
    images = describeImagesWithFilter(event['aminame'])
    _, latestImage = findLatest(images)
    accounts = event['accounts']
    accountlist = accounts.split(',')
    deregisterAllButLatestImage(images)
    deleteSnapshot(images, exclude=latestImage)
    modifyImageAttributes(latestImage['ImageId'], accountlist)
    return {
        'statusCode': 200,
        'body': json.dumps("Rotated old AMIs and Shared newest AMI: " + latestImage['ImageId'])
    }

# Changes the Image Attributes to be shared with an account.
def modifyImageAttributes(amiId, accounts):
    client.modify_image_attribute(ImageId=amiId, OperationType='add', Attribute='launchPermission', UserIds=accounts)
    print(f"Shared Image: {amiId} with UserIds: {accounts}")