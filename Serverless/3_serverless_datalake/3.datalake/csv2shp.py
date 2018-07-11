import csv
import io
import os
import tarfile
from collections import OrderedDict
from typing import Dict

import boto3
import fiona
from fiona import crs
from moto import mock_s3
from shapely.geometry import Point, mapping

from .util.event_parser import EVENT_PARSER


def get_csv(name, tar):
    csv_name = [file for file in tar.getnames() if name in file][0]
    obj = tar.extractfile(csv_name).read().decode('utf-8')
    return csv.DictReader(io.StringIO(obj))


def get_tree_data(csv_reader):
    return


def get_point_data(csv_reader):
    for c in csv_reader:
        print(c)
    return


def get_point_data(point_csv):
    """
    구간, 경도,위도정보가 담긴 csv파일에서 구간을 key로 하는 딕셔너리 생성
    :return:
    """
    data = {}
    for point in point_csv:
        data[int(point['구간'])] = {
            '경도': float(point['경도']),
            '위도': float(point['위도']),
            '고도': int(point['고도'])
        }
    return data


def make_record(properties: Dict[str, type], load_num: str, tree_row: Dict[str, str], point: Dict[str, str]):
    """
    shp 파일에 입력할 수목 정보 생성
    :return:
    """
    # 레코드 기본 구조
    record = {'properties': {"탐방로": load_num}, 'geometry': None}
    # 수목 정보 입력
    for key, value in zip(tree_row.keys(), tree_row.values()):
        atr_type = properties[key]
        # 속성 타입이 int인데 속성값이 ''일 경우 0으로 입력
        record['properties'][key] = atr_type(value) if value or atr_type is str else 0

    # 위치정보 입력
    record['properties']['경도'] = point['경도']
    record['properties']['위도'] = point['위도']
    record['properties']['고도'] = point['고도']
    record['geometry'] = mapping(Point(point['경도'], point['위도']))
    print(record)
    return record


def make_shp(tree_csv, points):
    """
    수목정보와 좌표정보를 매칭시켜 shp파일을 생성합니다
    :param tree_csv:
    :param points:
    :return:
    """
    shp_driver = 'ESRI Shapefile'
    properties = OrderedDict([
        # tree_csv에서 가져올 정보
        ('탐방로', str), ('구간', int), ('좌우', str), ('종명', str), ('개화', int), ('결실', int), ('비고', str),
        # point_csv에서 가져올 정보
        ('경도', float), ('위도', float), ('고도', int)
    ])
    # 타입별 기본값
    shp_schema = {
        #
        'properties': [(atr, properties[atr].__name__) for atr in properties],
        'geometry': 'Point'
    }
    shp_crs = crs.from_epsg(4326)
    with fiona.open('/tmp/sample.shp', 'w', encoding="utf-8", driver=shp_driver, schema=shp_schema, crs=shp_crs) as shp:
        for row in tree_csv:
            # 구간 번호
            point_num = int(row['구간'])
            # 수목의 구간번호에 매칭하는 좌표 정보
            point_info = points[point_num]
            # shp에 입력될 형식
            record = make_record(properties, 1, row, point_info)
            shp.write(record)


def get_tar(s3):
    data = s3.object.get()['Body']
    # 압축파일 가져오기
    with io.BytesIO(data.read()) as buffer:
        tar = tarfile.open(fileobj=buffer)
        # csv파일 압축 해제
        tree = get_csv('tree', tar)
        point = get_csv('point', tar)
    return tree, point


def handler(event, context):
    event = EVENT_PARSER(event)

    if event.s3:
        for s3 in event.records:
            # s3의 tar.gz 파일에서 수목,좌표 csv 객체 압축 해제
            tree_csv, point_csv = get_tar(s3)
            points = get_point_data(point_csv)
            shp = make_shp(tree_csv, points)

            trees = get_tree_data(tree_csv)

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
    handler(event, None)


if __name__ == '__main__':
    test()
