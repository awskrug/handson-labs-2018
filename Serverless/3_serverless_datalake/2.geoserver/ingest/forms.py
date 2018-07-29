import tarfile
import tempfile

from django import forms
from django.core.validators import FileExtensionValidator

from .util import get_bucket_name


def upload_file(prefix: str, file_obj, metadata: dict) -> bool:
    bucket = get_bucket_name()
    # 아직 s3배포 전일 경우 배포 실패
    if bucket is None:
        return False

    return True


def __init__(self, path):
    self.tmp = tempfile.TemporaryFile()
    self.tarfile = tarfile.open(fileobj=self.tmp, mode='w:')
    self.tarfile.add(path, '.')
    self.tarfile.close()
    self.tmp.flush()
    self.tmp.seek(0)
    self.tarfile = tarfile.open(fileobj=self.tmp, mode='r:')


class S3UploadForm(forms.Form):
    description = forms.CharField(max_length=50, required=True, help_text="자료에 대한 간단한 설명을 적어주요")
    uploader = forms.CharField(max_length=10, required=True, help_text="업로더 이름을 입력하세요")
    research_date = forms.CharField(required=True, help_text="조사 날짜")


class CsvUploadForm(S3UploadForm):
    point_csv = forms.FileField(required=True,
                                validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                help_text='gps 좌표 정보가 담긴 csv파일')
    info_csv = forms.FileField(required=True,
                               validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                               help_text='수목 정보가 담긴 csv파일')

    def upload(self):
        tmp = tempfile.TemporaryFile()
        print(type(self.point_csv), self.point_csv)
        print(type(self.info_csv), self.point_csv)
        print(self.description, self.uploader, self.research_date)
        # with tarfile.open(fileobj=tmp) as tar:
        #     tar
        # result = upload_file('csv', tmp, {})
        return


class ShpUploadForm(S3UploadForm):
    shp = forms.FileField(required=True,
                          validators=[FileExtensionValidator(allowed_extensions=['shp'])],
                          help_text="shp 파일")
    shx = forms.FileField(required=True,
                          validators=[FileExtensionValidator(allowed_extensions=['shx'])],
                          help_text="shx 파일")
    dbf = forms.FileField(required=True,
                          validators=[FileExtensionValidator(allowed_extensions=['dbf'])],
                          help_text="dbf 파일")
    prj = forms.FileField(required=True,
                          validators=[FileExtensionValidator(allowed_extensions=['prj'])],
                          help_text="prj 파일")

    def upload(self):
        return upload_file('shp', None, {})
