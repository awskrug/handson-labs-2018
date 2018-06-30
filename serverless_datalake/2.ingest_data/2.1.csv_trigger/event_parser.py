import ast
import base64
import io
import json
import tarfile
import zlib

import boto3

s3 = boto3.resource('s3')


def get_value_type(dic):
    """
    타입:값 형삭의 dyanmodb 필드에서 실제값을 추출
    :param dic:
    :return:
    """
    return list(dic.keys())[0]


def get_value(dic):
    return dic[get_value_type(dic)]


def get_map_value(data):
    raw = get_value(data)
    for k in raw:
        raw[k] = get_value(raw[k])
    return raw


class BaseParser:
    def set_data(self, data):
        [setattr(self, key, value) for key, value in zip(data.keys(), data.values())]


class DynamoStream:
    def __init__(self, record):
        self.raw = record
        self.action = self.raw.get('eventName')
        new_img = self.raw['dynamodb'].get('NewImage')
        old_img = self.raw['dynamodb'].get('OldImage')

        self.new_img = self.get_img(new_img) if new_img else None
        self.old_img = self.get_img(old_img) if old_img else None

    def get_img(self, data):
        """
        {key:{type:value}} 형식을 {key: value} 형식으로 변경
        :param data:
        :return:
        """
        info = {}
        for key in data:
            # todo: 추후 여러 타입을 지원하도록 구조 변경
            value_type = get_value_type(data[key])
            if value_type == 'L':
                value = []
                for v in get_value(data[key]):
                    if get_value_type(v) == 'M':
                        value.append(get_map_value(v))
                    else:
                        value.append(get_value(v))
            elif value_type == 'M':
                value = get_map_value(data[key])
            else:
                value = get_value(data[key])
            info[key] = value
        return info


# lambda event 파싱 클래스
class SnsEvent:
    def __init__(self, record, client):
        self.raw = record
        self.client = client
        self.EventSubscriptionArn = self.raw.get('EventSubscriptionArn')
        self.data = self.raw['Sns']
        self.TopicArn = self.data.get('TopicArn')
        self.msg = ast.literal_eval(self.data['Message'])
        self.get_msg_atrs()

    def get_msg_atrs(self):
        # 메시지 속성 가져오기
        self.msg_atrs = self.data.get('MessageAttributes')

        if self.msg_atrs:
            for k in self.msg_atrs:
                setattr(self, k, self.msg_atrs[k]['Value'])


# S3 파싱 클래스
class S3:
    def __init__(self, record):
        self.raw = record
        self.bucket = self.raw['s3']['bucket']
        self._object = self.raw['s3']['object']
        self.object_key = self._object['key']
        self.object_size = self._object['size']

        self.bucket_arn = self.bucket['arn']
        self.bucket_name = self.bucket['name']
        self.region = self.raw['awsRegion']
        self.object = s3.Object(self.bucket_name, self.object_key)

    def get_tar(self):
        data = self.object.get()['Body']
        with io.BytesIO(data.read()) as buffer:
            tar = tarfile.open(fileobj=buffer)
        return tar


class Kinesis(BaseParser):
    def __init__(self, record):
        self.raw = record
        kinesis = record.pop('kinesis')
        self.set_data(record)
        self.set_data(kinesis)


records_event_parser = {
    "Sns": {
        'name': 'sns',
        'parser': SnsEvent,
    },
    "dynamodb": {
        'name': 'dynamodb',
        'parser': DynamoStream,
    },
    "s3": {
        'name': 's3',
        'parser': S3,
    },
    "kinesis": {
        'name': 'kinesis',
        'parser': Kinesis,
    }
}


class EVENT_PARSER(BaseParser):
    def __init__(self, event):
        self.raw_event = event
        self.event_type = ''
        self.records = []
        self.apig = False
        self.scheduled_event = False
        self.check_event()
        self.support_event_type = ['apig', 's3', 'logs', 'kinesis', 'sns', 'dynamodb']
        for event_type in self.support_event_type:
            setattr(self, event_type, False if self.event_type != event_type else True)

    def check_event(self):
        """
        요청받은 이벤트의 종류 분리
        :return:
        """
        base_parser = {
            "Records": self.check_records_event,
            "detail-type": self.get_scheduled_event,
            "awslogs": self.get_logs_event,
            "headers": self.get_apig_event,
        }
        for key in base_parser.keys():
            if key in self.raw_event.keys():
                base_parser[key]()
                continue

    def check_records_event(self):
        # detect service
        records = self.raw_event['Records']
        record_keys = records[0].keys()
        event = [event for event in records_event_parser.keys() if event in record_keys][0]
        self.event_type = records_event_parser[event]['name']
        parser = records_event_parser[event]['parser']
        self.records += [parser(r) for r in records]

    def get_scheduled_event(self):
        self.event_type = "scheduled_event"
        self.set_data(self.raw_event)

    def get_logs_event(self):
        self.event_type = 'awslogs'
        self.data = zlib.decompress(base64.b64decode(self.raw_event['awslogs']['data']),
                                    16 + zlib.MAX_WBITS).decode('utf-8')

    @property
    def eval_data(self):
        """
        for logs dict to str data
        :return:
        """
        return ast.literal_eval(self.data)

    @property
    def json_data(self):
        """
        for logs dict to json data
        :return:
        """
        return json.loads(self.data)

    def get_apig_event(self):
        self.event_type = 'apig'
        self.headers = self.raw_event['headers']
        self.body = self.raw_event['body']
