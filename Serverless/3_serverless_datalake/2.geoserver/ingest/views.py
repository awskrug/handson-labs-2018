# Create your views here.
import os
import shutil
import tarfile
import tempfile
from datetime import datetime

import boto3
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic.edit import FormView

from .forms import CsvUploadForm, ShpUploadForm
from .util import get_bucket_name, get_prefix_obj_list, make_hashid, reset_s3

s3 = boto3.resource('s3')
s3_cli = boto3.client('s3')


def upload_file(key: str, tmp_name, metadata: dict = None) -> bool:
    bucket = get_bucket_name()
    # 아직 s3배포 전일 경우 배포 실패
    if bucket is None:
        return False
    metadata = metadata or {}
    metadata['upload_by'] = "geoserver"
    with open(tmp_name, 'rb') as file:
        s3.Object(bucket, key).put(
            Body=file.read(),
            ContentEncoding="gzip",
            Metadata=metadata
        )
    return True


def get_file_list(bucket, prefix):
    objs = get_prefix_obj_list(bucket, prefix)
    result = []
    if objs:
        for obj in objs:
            obj_info = s3_cli.get_object(
                Bucket=bucket,
                Key=obj,
            )
            result.append({
                "key_name": obj.split('/')[-1],
                "timestamp": obj_info['LastModified'],
                "metadata": obj_info['Metadata']
            })
    return result or None


class UploadView(FormView):
    def save_to_tmp(self, obj):
        tmp_obj = tempfile.NamedTemporaryFile(delete=False)
        with open(tmp_obj.name, 'wb') as f:
            shutil.copyfileobj(obj, f)
        return tmp_obj

    def make_tar_gz(self, files: dict):
        """
        파일 목록을 받아 각각 임시 파일로 저장후 압축파일 생성
        :param files: { "파일명":file_obj }
        :return:
        """
        save_files = {name: self.save_to_tmp(file).name for name, file in zip(files.keys(), files.values())}
        tar_file = tempfile.NamedTemporaryFile(delete=False)
        with tarfile.open(tar_file.name, mode='w:gz') as tar:
            for name, tmp_name in zip(save_files.keys(), save_files.values()):
                tar.add(tmp_name, arcname=name)
        return tar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # s3버킷 상태 추가
        bucket = get_bucket_name()

        if bucket:
            bucket_url = f"https://s3.console.aws.amazon.com/s3/buckets/{bucket}/"
            obj_url_prefix = f"https://s3.console.aws.amazon.com/s3/object/{bucket}"
            context['bucket_name'] = bucket
            context['bucket_url'] = bucket_url
            context['obj_url_prefix'] = obj_url_prefix
            context["csv_files"] = get_file_list(bucket, 'csv')
            context["csv_url"] = f"{bucket_url}csv/"
            context["shp_files"] = get_file_list(bucket, 'shp')
            context['shp_url'] = f"{bucket_url}shp/"
            context["json_files"] = get_file_list(bucket, 'json')
            context["json_url"] = f"{bucket_url}json/"

        return context


class CsvUploadView(UploadView):
    template_name = 'ingest/csv.html'
    form_class = CsvUploadForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            context = self.get_context_data()
            context['sucess'] = False
            return TemplateResponse(self.request, self.template_name, context=context)
        hash_name = make_hashid()
        tar_file = self.make_tar_gz({
            "point.csv": form.files['point_csv'],
            "tree.csv": form.files['info_csv'],
        })
        metadata = {
            "description": form.data['description'],
            "uploader": form.data['uploader'],
            "research_date": form.data['research_date']
        }
        key = f"csv/{hash_name}.tar.gz"
        context = self.get_context_data()
        if upload_file(key, tar_file.name, metadata=metadata):
            context['success'] = True
            return TemplateResponse(self.request, self.template_name, context=context)
        else:
            context['success'] = False
            return TemplateResponse(self.request, self.template_name, context=context)


class ShpUploadView(UploadView):
    template_name = 'ingest/shp.html'
    form_class = ShpUploadForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        hash_name = make_hashid()
        tar_file = self.make_tar_gz({
            f"{hash_name}.shp": form.files['shp'],
            f"{hash_name}.shx": form.files['shx'],
            f"{hash_name}.dbf": form.files['dbf'],
            f"{hash_name}.prj": form.files['prj'],
            f"{hash_name}.cpg": form.files['cpg'],
        })
        metadata = {
            "description": form.data['description'],
            "uploader": form.data['uploader'],
            "research_date": form.data['research_date']
        }
        key = f"shp/{hash_name}.tar.gz"
        context = self.get_context_data()
        if upload_file(key, tar_file.name, metadata=metadata):
            context['success'] = True
            return TemplateResponse(self.request, self.template_name, context=context)
        else:
            context['success'] = False
            return TemplateResponse(self.request, self.template_name, context=context)


def reset_csv_s3(request):
    reset_s3('csv')
    context = {
        'form': CsvUploadForm(),
        'reset_success': "csv 폴더를 초기화 했습니다",
        's3_console_url': "https:/asd.com",
        'ddb_console_url': "https:/asd.com"
    }
    return TemplateResponse(request, 'ingest/csv.html', context=context)


def reset(request):
    reset_s3()
    redirect_to = request.GET.get('next', '')
    if redirect_to:
        return redirect(redirect_to)
    return redirect("ingest:home")


def upload_all(request):
    reset_s3()
    bucket = get_bucket_name()
    if bucket:
        for file in files:
            with open(file, 'rb') as f:
                s3.Object(bucket, f"shp/{file.split('/')[-1]}").put(
                    Body=f.read(),
                    ContentEncoding="gzip",
                    Metadata={
                        'upload_by': 'geoserver',
                        'uploader': 'autoupload',
                        "description": 'auto upload shp file',
                        "research_date": f"{datetime.now()}"
                    }
                )
    return redirect("ingest:home")
