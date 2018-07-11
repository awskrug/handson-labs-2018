# Create your views here.
import boto3
from django.template.response import TemplateResponse
from django.views.generic.edit import FormView

from .forms import CsvUploadForm, ShpUploadForm
from .util import reset_s3


class UplaodView(FormView):
    def form_valid(self, form):
        form.upload()
        context = self.get_context_data()
        context['success'] = True
        return TemplateResponse(self.request, self.template_name, context=context)


class CsvUploadView(UplaodView):
    template_name = 'ingest/csv.html'
    form_class = CsvUploadForm
    pass


class ShpUploadView(UplaodView):
    template_name = 'ingest/shp.html'
    form_class = ShpUploadForm
    pass


def reset_csv_s3(request):
    reset_s3('csv')
    context = {
        'form': CsvUploadForm(),
        'reset_success': "csv 폴더를 초기화 했습니다",
        's3_console_url': "https:/asd.com",
        'ddb_console_url': "https:/asd.com"
    }
    print(context)
    return TemplateResponse(request, 'ingest/csv.html', context=context)


def reset_shp_s3(request):
    reset_s3('shp')
    context = {
        'form': CsvUploadForm(),
        'reset_success': "shp 폴더를 초기화 했습니다",
        's3_console_url': "https:/asd.com",
        'ddb_console_url': "https:/asd.com"
    }
    return TemplateResponse(request, 'ingest/shp.html', context=context)
