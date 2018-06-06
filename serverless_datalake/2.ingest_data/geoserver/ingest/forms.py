from django import forms
from django.core.validators import FileExtensionValidator


class S3UploadForm(forms.Form):
    description = forms.CharField(max_length=50, required=True,help_text="자료에 대한 간단한 설명을 적어주세요")
    uploader = forms.CharField(max_length=10, required=True,help_text="업로더 이름을 입력하세요")


class CsvUploadForm(S3UploadForm, forms.Form):
    point_csv = forms.FileField(required=True,
                                validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    info_csv = forms.FileField(required=True,
                               validators=[FileExtensionValidator(allowed_extensions=['csv'])])
