#!/bin/bash
set -ex

# Infer variables from build.sh, no need to modify them in both locations.
APPNAME="$(grep APPNAME= build.sh | cut -d '"' -f2)"
LAMBDACODEBUCKET="$(grep LAMBDACODEBUCKET= build.sh | cut -d '"' -f2)"
PREFIX="$(grep PREFIX= build.sh | cut -d '"' -f2)"

buildAmiLATESTVERSION=$(aws s3api list-object-versions --bucket $LAMBDACODEBUCKET --prefix $PREFIX/buildAmi.zip | jq '.Versions[] | select(.IsLatest==true)' | jq -r .VersionId)
rotateAmiLATESTVERSION=$(aws s3api list-object-versions --bucket $LAMBDACODEBUCKET --prefix $PREFIX/rotateAmi.zip | jq '.Versions[] | select(.IsLatest==true)' | jq -r .VersionId)
DestSubnetId="subnet-0608463b2ef22881b"
ImageBuilderVPCId="vpc-0e7574aadd97d2011"
KeyName="BRYANLABS-AWS"
AuthorizedKey="CHANGEME"

export APPNAME LAMBDACODEBUCKET PREFIX LATESTVERSION DestSubnetId SecurityGroupId KeyName AuthorizedKey

# Download template from Source
aws s3 cp "s3://$LAMBDACODEBUCKET/$PREFIX/$APPNAME".yml .


# Check File Size
SIZE=$(wc -c "$APPNAME".yml | cut -d ' ' -f1)

# Set CLI Options
CLI_OPTIONS="--parameters \
    ParameterKey=Prefix,ParameterValue=$PREFIX \
    ParameterKey=DestSubnetId,ParameterValue=$DestSubnetId \
    ParameterKey=ImageBuilderVPCId,ParameterValue=$ImageBuilderVPCId \
    ParameterKey=KeyName,ParameterValue=$KeyName \
    ParameterKey=buildAmilatestVersion,ParameterValue=$buildAmiLATESTVERSION \
    ParameterKey=rotateAmilatestVersion,ParameterValue=$rotateAmiLATESTVERSION \
    ParameterKey=AuthorizedKey,ParameterValue=$AuthorizedKey \
    ParameterKey=lambdaCodeBucket,ParameterValue=$LAMBDACODEBUCKET"

S3URL="https://s3.amazonaws.com"
export CLI_OPTIONS CLI_OPTIONS S3URL

# Handle Large CFTs

if (( SIZE > 51200 )); then
    if aws cloudformation describe-stacks --stack-name $APPNAME > /dev/null; then
        aws cloudformation update-stack --stack-name "$APPNAME" --template-url "$S3URL/$LAMBDACODEBUCKET/$PREFIX/$APPNAME".yml \
        --capabilities CAPABILITY_NAMED_IAM $CLI_OPTIONS
    else
        aws cloudformation create-stack --stack-name "$APPNAME" --template-url "$S3URL/$LAMBDACODEBUCKET/$PREFIX/$APPNAME".yml \
        --capabilities CAPABILITY_NAMED_IAM $CLI_OPTIONS
    fi
    
else
    if aws cloudformation describe-stacks --stack-name $APPNAME > /dev/null; then
        aws cloudformation update-stack --stack-name "$APPNAME" --template-body "file://$APPNAME".yml \
        --capabilities CAPABILITY_NAMED_IAM $CLI_OPTIONS
    else
        aws cloudformation create-stack --stack-name "$APPNAME" --template-body "file://$APPNAME".yml \
        --capabilities CAPABILITY_NAMED_IAM $CLI_OPTIONS
    fi
fi

rm -rf "$APPNAME".yml