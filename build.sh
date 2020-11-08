#!/bin/bash
set -e

APPNAME="AmiFactory"
LAMBDACODEBUCKET="altitude-installers"
PREFIX="amifactory"

#Build the Lambda Executable and archive.
echo "### Building for Lambda."
cd buildAmi
zip -r9 ../buildAmi.zip .
cd ..

#Build the Lambda Executable and archive.
echo "### Building RotateAmi for Lambda."
cd rotateAmi
zip -r9 ../rotateAmi.zip .
cd ..

# Upload lambda function code to S3.
aws s3 cp buildAmi.zip s3://$LAMBDACODEBUCKET/$PREFIX/
aws s3 cp rotateAmi.zip s3://$LAMBDACODEBUCKET/$PREFIX/
echo "### Uploading Lambda Code to S3."
sleep 1
rm -rf "${APPNAME}.zip" buildAmi.zip
rm -rf "${APPNAME}.zip" rotateAmi.zip

# Upload CFT to S3.
aws s3 cp cloudformation.yml s3://$LAMBDACODEBUCKET/$PREFIX/$APPNAME.yml
