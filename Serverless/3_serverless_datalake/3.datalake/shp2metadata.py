import json
import json
import os
import tarfile
from datetime import datetime, timezone
from os import path

import boto3
import fiona
from pynamodb.attributes import NumberAttribute, UTCDateTimeAttribute, UnicodeAttribute, \
    UnicodeSetAttribute
from pynamodb.models import Model

try:
    from util.event_parser import EVENT_PARSER
except Exception:
    from .util.event_parser import EVENT_PARSER

tmp = "/tmp"

db_name = os.environ.get('MetaDataDB')


class MetaData(Model):
    class Meta:
        table_name = db_name
        region = "ap-northeast-2"
        read_capacity_units = 1
        write_capacity_units = 1

    file = UnicodeAttribute(hash_key=True)
    timestamp = UTCDateTimeAttribute(range_key=True, default=datetime.now(tz=timezone.utc))
    trees_count = NumberAttribute(null=True)
    species = UnicodeSetAttribute(null=True)
    species_count = UnicodeAttribute(null=True)
    min_num = NumberAttribute(null=True)
    max_num = NumberAttribute(null=True)
    min_height = NumberAttribute(null=True)
    max_height = NumberAttribute(null=True)
    description = UnicodeAttribute(null=True)
    upload_by = UnicodeAttribute(null=True)
    uploader = UnicodeAttribute(null=True)


def make_dir(dir_name):
    if not path.isdir(dir_name):
        os.mkdir(dir_name)


make_dir(f"{tmp}/shp")
s3 = boto3.client('s3')


def get_meta(shp_file):
    """
    shp 파일을 json 형식으로 변경합니다
    :param shp_file: 변경할 shp 파일명
    :return: 변경된 json 파일명
    """
    metadata = {}
    with fiona.open(shp_file, encode="utf-8") as shp:
        metadata['trees_count'] = len(shp)
        metadata['species'] = set()
        metadata['species_count'] = dict()
        metadata['min_num'] = None
        metadata['max_num'] = None
        metadata['min_height'] = None
        metadata['max_height'] = None
        for record in shp:
            print(record)
            properites = record['properties']
            species = properites.get('종명')

            num = properites.get('구간')
            height = properites.get('고도')

            if species and not species == '-':
                if species in metadata['species']:
                    metadata['species_count'][species] += 1
                else:
                    metadata['species_count'][species] = 1
                metadata['species'].add(species)

            if num is None:
                pass
            elif metadata['min_num'] is None:
                metadata['min_num'] = num
                metadata['max_num'] = num
            else:
                metadata['min_num'] = min(num, metadata['min_num'])
                metadata['max_num'] = max(num, metadata['max_num'])

            if height is None:
                pass
            elif metadata['min_height'] is None:
                metadata['min_height'] = height
                metadata['max_height'] = height
            else:
                metadata['min_height'] = min(height, metadata['min_height'])
                metadata['max_height'] = max(height, metadata['max_height'])
        if metadata['species_count']:
            metadata['species_count'] = json.dumps(metadata['species_count'], ensure_ascii=False)
    return metadata


def shp2meta(s3_obj):
    tmp_file = path.join(tmp, s3_obj.object_key)
    file_name = s3_obj.object_key.split('.')[0]
    # 파일 다운로드
    with open(tmp_file, 'wb') as data:
        s3_obj.object.download_fileobj(data)

    # 압축 해제
    extract_dir = path.join(tmp, file_name)
    make_dir(extract_dir)
    with tarfile.open(tmp_file) as tar:
        tar.extractall(extract_dir)

    # json 파일로 변경
    shp_file = [path.join(extract_dir, name) for name in os.listdir(extract_dir) if name.split('.')[-1] == "shp"][0]
    metadata = get_meta(shp_file)
    s3_meta = s3_obj.object.get()['Metadata']
    filter_keys = ['upload_by', 'uploader', 'description']
    for k in filter_keys:
        for key in s3_meta:
            if k in key:
                metadata[k] = s3_meta[key]
                continue
    record = MetaData(hash_key=s3_obj.object_key, **metadata)
    record.save()


def process_s3(records):
    print(records)
    for s3 in records:
        shp2meta(s3)


def process_sns(records):
    for raw_sns_event in records:
        s3_event = EVENT_PARSER(json.loads(raw_sns_event.data['Message']))
        if s3_event.s3:
            process_s3(s3_event.records)


def handler(raw_event, context):
    # s3 -> sns -> sqs 순으로 보내진 이벤트를
    # sqs -> sns -> s3 순으로 역으로 이벤트 파싱
    print(raw_event)
    sns_event = EVENT_PARSER(raw_event)
    if sns_event.sns:
        process_sns(sns_event.records)
