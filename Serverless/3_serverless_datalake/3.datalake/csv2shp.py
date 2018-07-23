import csv
import gzip
import io
import shutil
import tarfile
from collections import OrderedDict
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Dict

import boto3
import fiona
from fiona import crs
from hashids import Hashids
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
    shp = fiona.open('/tmp/sample.shp', 'w', encoding="utf-8", driver=shp_driver, schema=shp_schema, crs=shp_crs)
    for row in tree_csv:
        # 구간 번호
        point_num = int(row['구간'])
        # 수목의 구간번호에 매칭하는 좌표 정보
        point_info = points[point_num]
        # shp에 입력될 형식
        record = make_record(properties, 1, row, point_info)
        shp.write(record)
    return shp


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
            f = NamedTemporaryFile()
            gz = gzip.open(f, 'wb')
            shutil.copyfileobj(f, gz)

            meta = {
                "origin_data_bucket": s3.bucket_arn,
                "origin_data_key": s3.object_key,
            }
            dt = datetime.utcnow()
            file_name = f"{Hashids(s3.object_key).encode(dt.year, dt.month, dt.day)}.gz"
            s3_resource = boto3.resource('s3')
            s3_resource.Object(s3.bucket_name, file_name).put(Body=gz, ContentEncoding="gzip",
                                                              Metadata=meta)
            shp.close()
            gz.close()

    return 'hellow'
