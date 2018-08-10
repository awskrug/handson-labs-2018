import tarfile
import tempfile
from datetime import datetime

import boto3
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

s3 = boto3.resource('s3')


def __init__(self, path):
    self.tmp = tempfile.TemporaryFile()
    self.tarfile = tarfile.open(fileobj=self.tmp, mode='w:')
    self.tarfile.add(path, '.')
    self.tarfile.close()
    self.tmp.flush()
    self.tmp.seek(0)
    self.tarfile = tarfile.open(fileobj=self.tmp, mode='r:')


def is_ascii(value):
    try:
        value.encode('ascii')
    except UnicodeEncodeError:
        raise ValidationError('영어로만 입력해주세요')


class OnlyAsciiField(forms.CharField):
    default_validators = [is_ascii]


def default():
    return f"{datetime.today()} upload file from geoserver"


class S3UploadForm(forms.Form):
    description = OnlyAsciiField(max_length=50, required=True, help_text="자료에 대한 간단한 설명을 영어로 적어주요",
                                 )
    uploader = OnlyAsciiField(max_length=10, required=True, help_text="업로더 이름을 영어로 입력하세요")
    research_date = forms.CharField(required=True, help_text="조사 날짜")


class CsvUploadForm(S3UploadForm):
    point_csv = forms.FileField(required=True,
                                validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                help_text='gps 좌표 정보가 담긴 csv파일')
    info_csv = forms.FileField(required=True,
                               validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                               help_text='수목 정보가 담긴 csv파일')


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
    cpg = forms.FileField(required=True,
                          validators=[FileExtensionValidator(allowed_extensions=['cpg'])],
                          help_text="cpg 파일")
