from datetime import datetime

import boto3
from django.conf import settings
from hashids import Hashids

hashid = Hashids(alphabet='abcdefghijklmnopqrstuvwxyz123456789')
s3 = boto3.resource('s3')

cloudformation = boto3.resource('cloudformation')


def make_hashid():
    now = datetime.utcnow()
    return hashid.encode(now.year, now.month, now.day, now.hour, now.minute, now.microsecond)


def get_bucket_name():
    """
    cloudformation 내보내기 값에서 버킷 이름 가져옴
    :return:
    """
    export_name = settings.BUCKET_EXPORT_NAME
    try:
        stack = cloudformation.Stack(settings.CFN_STACK_NAME)
        for out in stack.outputs:
            if out.get('ExportName') == export_name:
                return out['OutputValue']
    except Exception:
        pass
    return None


def get_prefix_obj_list(bucket, prefix):
    result = []
    bucket = s3.Bucket(bucket)
    for obj in bucket.objects.filter(Prefix=f"{prefix}/"):
        result.append(obj.key)
    return result


def reset_s3():
    """
    path의 모든 파일을 삭제 합니다
    :param path: 리셋할 s3 경로
    :return:
    """
    bucket = get_bucket_name()

    if bucket:
        bucket = boto3.resource('s3').Bucket(bucket)
        delete_objs = []
        for prefix in ['csv', 'shp', 'json']:
            for obj in bucket.objects.filter(Prefix=f'{prefix}/'):
                delete_objs.append({"Key": obj.key})

        if delete_objs:
            bucket.delete_objects(
                Delete={
                    'Objects': delete_objs
                }
            )
