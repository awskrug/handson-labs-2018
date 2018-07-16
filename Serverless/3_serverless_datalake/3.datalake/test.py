from datetime import datetime, timezone
from os import path
from unittest import TestCase

import boto3
from moto import mock_dynamodb2, mock_s3

csv_s3 = 'csv_s3'
shp_S3 = 'shp_s3'
json_S3 = 'json_s3'
base_dir = path.abspath(path.dirname(__file__))
mock_dir = path.join(base_dir, "mock")


class LambdaTestCase(TestCase):

    def s3_event(self, bucket_name, obj_key):
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
                            "key": obj_key,
                            "size": 1024
                        },
                        "bucket": {
                            "arn": "",
                            "name": bucket_name,
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
        return event

    def sns_event(self, msg):
        event = {
            'Records': [{
                'EventSource': 'aws:sns', 'EventVersion': '1.0',
                'EventSubscriptionArn': 'arn:aws:sns:ap-northeast-2:615532562228:awscodestar-upowetland-'
                                        'lambda-UpoDataArticleIngestNoti-15HI3AEDZZ9RA:516df007-5df8-46e2'
                                        '-8344-dd3d9b3e4c2e',
                'Sns': {
                    'Type': 'Notification', 'MessageId': 'c93c1750-7ac9-533f-895e-4436eabaddd9',
                    'TopicArn': 'arn:aws:sns:ap-northeast-2:615532562228:awscodestar-upowetland-'
                                'lambda-UpoDataArticleIngestNoti-15HI3AEDZZ9RA',
                    'Subject': 'Amazon S3 Notification',
                    'Message': f'{msg}',
                    'Timestamp': '2018-05-04T16:45:39.537Z', 'SignatureVersion': '1',
                    'Signature': 'CY+zcJvITrDAaaXB2hdzfDjGcGcdwFiqAb6AXo54Xssyc3BoZuEZ8W/UrLkZYZ5rfRF'
                                 'XbeAigdlalEtdamZfSpAtADEeLKo7ICN2wtXbp8H4XtEXcG7yPnX5cqiTM6oWHLBV/H'
                                 'BwFHYY2gxOGhyUhsGx8HOPOQVsRAyBs+g4b69kKDI55v7gEmwne4bbSyAxQKxQxM33Y'
                                 'zHnSPd/DDSv7ME+56TLFfJkR8/mmB1GQ4rgGhY/23f64fVF4orf9RakijYK414PXNbP'
                                 'SSZlXY0sDfL9JJzo7DxVIY28oM8FA1vWlYG2GnckjbG99Odw24Aa+AHf0nc6TDA8fkLAbqStRQ==',
                    'SigningCertUrl': 'https://sns.ap-northeast-2.amazonaws.com/SimpleNotificationSer'
                                      'vice-ac565b8b1a6c5d002d285f9598aa1d9b.pem',
                    'UnsubscribeUrl': 'https://sns.ap-northeast-2.amazonaws.com/?Action=Unsubscribe&S'
                                      'ubscriptionArn=arn:aws:sns:ap-northeast-2:615532562228:awscode'
                                      'star-upowetland-lambda-UpoDataArticleIngestNoti-15HI3AEDZZ9RA:'
                                      '516df007-5df8-46e2-8344-dd3d9b3e4c2e',
                    'MessageAttributes': {}
                }
            }]
        }
        return event

    def sqs_event(self, msg):
        event = {
            "Records": [
                {
                    "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
                    "receiptHandle": "aa",
                    "body": f"{msg}",
                    "attributes": {
                        "ApproximateReceiveCount": "3",
                        "SentTimestamp": "1529104986221",
                        "SenderId": "594035263019",
                        "ApproximateFirstReceiveTimestamp": "1529104986230"
                    },
                    "messageAttributes": {},
                    "md5OfBody": "9bb58f26192e4ba00f01e2e7b136bbd8",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:us-west-2:594035263019:NOTFIFOQUEUE",
                    "awsRegion": "us-west-2"
                }
            ]
        }

        return event

    def upload_data_file(self, mock_file: str, Bucket: str, obj_key: str, **metadata):
        """
        목업 파일을 s3 업로드후 이벤트 메시지 생성
        :param mock_file: 파일 경로
        :return: S3 Put 이벤트 메시지
        """
        s3 = boto3.client('s3')
        create_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        with open(mock_file, 'rb') as f:
            s3.put_object(
                Body=f.read(),
                Bucket=Bucket,
                Key=obj_key,
                Metadata={
                             'content-type': 'text/json',
                             'content-encodding': 'gzip',
                             'create-timestamp': create_timestamp,
                         } + metadata
            )
        return self.s3_event(Bucket, obj_key)

    def s3_to_sns_event(self, s3_put_msg):
        """
        s3 put 이벤트 메시지를 sns로 보냈을때 람다가 받는 이벤트 메시지 생성
        :param msg:
        :return:
        """
        return self.sns_event(s3_put_msg)

    def s3_to_sns_to_sqs_event(self, s3_put_msg):
        return self.sqs_event(self.sns_event(s3_put_msg))

    def start_mock(self):
        self.mock_s3 = mock_s3()
        self.mock_ddb = mock_dynamodb2()
        self.mock_s3.start()
        self.mock_ddb.start()

        self.csv_bucket = csv_s3
        self.shp_bucket = shp_S3
        self.json_bucket = json_S3

        self.s3 = boto3.client('s3')
        self.s3.create_bucket(Bucket=self.csv_bucket)
        self.s3.create_bucket(Bucket=self.shp_bucket)
        self.s3.create_bucket(Bucket=self.json_bucket)

    def stop_mock(self):
        self.mock_s3.stop()
        self.mock_ddb.stop()

    def setUp(self):
        self.start_mock()
        self.setUpExt()

    def tearDown(self):
        self.tearDownExt()
        self.stop_mock()

    def setUpExt(self):
        """
        setUp 확장 메소드 - 기존의 setUp 대체
        :return:
        """
        pass

    def tearDownExt(self):
        """
        tearDown 확장 메소드- 기존의 tearDown 대체
        :return:
        """
        pass


class Csv2ShpTestCase(LambdaTestCase):

    def setUpExt(self):
        self.mock_data = path.join(mock_dir, "csv.tar.gz")
        self.mock_obj_key = "mock_csv.tar.gz"
        self.research_data = "1993-09-22"
        self.researcher = "mr.lambda"
        self.description = "this is mock file"
        self.mock_metadata = {
            "x-amz-meta-research-date": self.research_data,
            "x-amz-meta-researcher": self.researcher,
            "x-amz-meta-description": self.description
        }
        self.mock_event = self.upload_data_file(self.mock_data, self.csv_bucket, self.mock_obj_key, **self.mock_metadata)

    def tearDownExt(self):
        pass

    def test_handler(self):
        from ..csv2shp import handler
        result = handler(self.mock_event)
        self.assertEqual('hi',result)
        print(result)
        return
# @mock_s3
# def test():
#     bucket = 'test_bucket'
#     file_name = 'data.tar.gz'
#     s3 = boto3.client('s3', region_name='ap-northeast-2')
#     BASE_DIR = os.path.dirname(__file__)
#     file = os.path.join(BASE_DIR, file_name)
#
#     conn = boto3.resource('s3', region_name='ap-northeast-2')
#     conn.create_bucket(Bucket=bucket)
#
#     with open(file, 'rb') as f:
#         s3.put_object(Bucket=bucket, Key=file_name, Body=f)
#     event = {
#         "Records": [
#             {
#                 "eventVersion": "2.0",
#                 "eventTime": "1970-01-01T00:00:00.000Z",
#                 "requestParameters": {
#                     "sourceIPAddress": "127.0.0.1"
#                 },
#                 "s3": {
#                     "configurationId": "testConfigRule",
#                     "object": {
#                         "eTag": "0123456789abcdef0123456789abcdef",
#                         "sequencer": "0A1B2C3D4E5F678901",
#                         "key": file_name,
#                         "size": 1024
#                     },
#                     "bucket": {
#                         "arn": '',
#                         "name": bucket,
#                         "ownerIdentity": {
#                             "principalId": "EXAMPLE"
#                         }
#                     },
#                     "s3SchemaVersion": "1.0"
#                 },
#                 "responseElements": {
#                     "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
#                     "x-amz-request-id": "EXAMPLE123456789"
#                 },
#                 "awsRegion": "us-east-1",
#                 "eventName": "ObjectCreated:Put",
#                 "userIdentity": {
#                     "principalId": "EXAMPLE"
#                 },
#                 "eventSource": "aws:s3"
#             }
#         ]
#     }
#     handler(event, None)
