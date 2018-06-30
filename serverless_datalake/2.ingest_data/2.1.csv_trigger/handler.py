import os

import boto3
from event_parser import EVENT_PARSER
from moto import mock_s3


def handler(event, context):
    event = EVENT_PARSER(event)
    if event.s3:
        for s3 in event.records:
            tar = s3.get_tar()

    return 'hi'


@mock_s3
def test():
    bucket = 'test_bucket'
    file_name = 'data.tar.gz'
    s3 = boto3.client('s3', region_name='ap-northeast-2')
    BASE_DIR = os.path.dirname(__file__)
    file = os.path.join(BASE_DIR, file_name)

    conn = boto3.resource('s3', region_name='ap-northeast-2')
    conn.create_bucket(Bucket=bucket)

    with open(file, 'rb') as f:
        s3.put_object(Bucket=bucket, Key=file_name, Body=f)
    event = {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "s3": {
                    "configurationId": "testConfigRule",
                    "object": {
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901",
                        "key": file_name,
                        "size": 1024
                    },
                    "bucket": {
                        "arn": '',
                        "name": bucket,
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        }
                    },
                    "s3SchemaVersion": "1.0"
                },
                "responseElements": {
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
                    "x-amz-request-id": "EXAMPLE123456789"
                },
                "awsRegion": "us-east-1",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "eventSource": "aws:s3"
            }
        ]
    }
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account

    handler(event, None)


if __name__ == '__main__':
    test()
