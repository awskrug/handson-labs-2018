import boto3
from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator

cloudformation = boto3.resource('cloudformation')



def get_bucket(resource):
    stack = cloudformation.Stack(settings.CFN_STACK_NAME).outputs
    # todo : stack에서 각 리소스(csv,shp등)별 버킷명 가져오기 - 2018-07-08
    return


class S3UploadForm(forms.Form):
    description = forms.CharField(max_length=50, required=True, help_text="자료에 대한 간단한 설명을 적어주요")
    uploader = forms.CharField(max_length=10, required=True, help_text="업로더 이름을 입력하세요")
    research_date = forms.CharField(required=True, help_text="조사 날짜")

    def is_valid(self):
        print(super().is_valid())
        print(self.__dict__)
        return super().is_valid()


class CsvUploadForm(S3UploadForm):
    point_csv = forms.FileField(required=True,
                                validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                help_text='gps 좌표 정보가 담긴 csv파일')
    info_csv = forms.FileField(required=True,
                               validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                               help_text='수목 정보가 담긴 csv파일')

    def upload(self):
        # todo : csv 업로드 함수 추가 - 2018-06-06
        bucket = get_bucket('csv')
        pass


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
        # todo : shp 업로드 함수 추가 - 2018-06-06
        bucket = get_bucket('shp')
