import gzip
import json
import os
import tarfile
from os import path

import boto3
import fiona

try:
    from util.event_parser import EVENT_PARSER
except Exception:
    from .util.event_parser import EVENT_PARSER

tmp = "/tmp"


def make_dir(dir_name):
    if not path.isdir(dir_name):
        os.mkdir(dir_name)


make_dir(f"{tmp}/shp")
s3 = boto3.client('s3')


def to_json(record):
    """
    shp파일의 개별 레코들를 json 형식으로 변경
    :param record:
    :return:
    """
    data = record['properties']
    geometry = record['geometry']['coordinates']
    data['경도'], data['위도'] = geometry
    return json.dumps(data, ensure_ascii=False)


def transform(shp_file):
    """
    shp 파일을 json 형식으로 변경합니다
    :param shp_file: 변경할 shp 파일명
    :return: 변경된 json 파일명
    """
    dir_name = path.dirname(shp_file)
    json_name = f"{shp_file.split('.')[0]}.json"
    json_file = path.join(dir_name, json_name)
    print("변환", dir_name, json_name, json_file)
    with fiona.open(shp_file, encode="utf-8") as shp:
        with open(json_file, 'w', encoding='utf-8') as f:
            for record in shp:
                f.write(to_json(record) + '\n')
    return json_file


def upload_s3(bucket, json_file, metadata):
    """
    파일을 gz하여 s3로 업로드
    :param json_file: 업로드할 json 파일명
    :return:
    """
    gz_name = f"{json_file}.gz"
    obj_key = f"json/{path.basename(gz_name)}"
    print("업로드", gz_name, obj_key)

    with open(json_file, 'rb') as f:
        gz = gzip.compress(f.read())
        s3.put_object(
            Body=gz,
            Bucket=bucket,
            ContentEncoding='gzip',
            ContentLanguage='string',
            ContentType='application/json',
            Key=obj_key,
            # todo : 메타데이터 추가 - 2018-07-28
            Metadata=metadata,
        )


def shp2json(s3_obj):
    tmp_file = path.join(tmp, s3_obj.object_key)
    file_name = s3_obj.object_key.split('.')[0]
    print('start shp2json', tmp_file, file_name)
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
    json_file = transform(shp_file)

    metadata = s3_obj.object.get()["Metadata"]
    origin_metadata_key = [key for key in metadata if "origin" not in key]
    for key in origin_metadata_key:
        metadata[f"origine_{key}"] = metadata.pop(key)
    metadata['upload_by'] = "shp2csv"
    metadata['origin_data_bucket'] = s3_obj.bucket_name
    metadata['origin_data_key'] = s3_obj.object_key
    # s3 업로드
    upload_s3(s3_obj.bucket_name, json_file, metadata)


def process_s3(records):
    for s3 in records:
        shp2json(s3)


def process_sns(event):
    s3_event = EVENT_PARSER(event)
    if s3_event.s3:
        process_s3(s3_event.records)


def process_sqs(records):
    for raw_sns_event in records:
        event = json.loads(raw_sns_event.body)
        if event['Type'] == 'Notification':
            process_sns(json.loads(event['Message']))


def handler(raw_event, context):
    # s3 -> sns -> sqs 순으로 보내진 이벤트를
    # sqs -> sns -> s3 순으로 역으로 이벤트 파싱
    print(raw_event)
    sqs_event = EVENT_PARSER(raw_event)
    if sqs_event.sqs:
        process_sqs(sqs_event.records)
