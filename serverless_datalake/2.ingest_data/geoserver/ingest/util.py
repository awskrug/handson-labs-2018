import boto3

s3 = boto3.client('s3')


def reset_s3(path):
    """
    path의 모든 파일을 삭제 합니다
    :param path: 리셋할 s3 경로
    :return:
    """
    pass
    # todo : s3 파일 초기화 코드 추가 - 2018-06-06