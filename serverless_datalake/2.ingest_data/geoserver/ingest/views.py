# Create your views here.
from django.template.response import SimpleTemplateResponse
from django.views.generic.edit import FormView

from .forms import CsvUploadForm
from .util import reset_s3

class CsvUploadView(FormView):
    template_name = 'ingest/csv.html'
    form_class = CsvUploadForm

    def form_valid(self, form):
        # todo : 파일 업로드 로직 추가 - 2018-06-06
        context = self.get_context_data()
        context['sucess'] = True
        return SimpleTemplateResponse('ingest/csv.html', context=context)



def reset_csv_s3(request):
    reset_s3('csv')
    context = {
        'form' : CsvUploadForm(),
        'reset_sucess': "csv 폴더를 초기화 했습니다",
        's3_console_url' : "https:/asd.com",
        'ddb_console_url': "https:/asd.com"
    }
    print(context)
    return SimpleTemplateResponse('ingest/csv.html', context=context)


def reset_shp_s3(request):
    reset_s3('shp')
    context = {
        'form': CsvUploadForm(),
        'reset_sucess': "csv 폴더를 초기화 했습니다",
        's3_console_url': "https:/asd.com",
        'ddb_console_url': "https:/asd.com"
    }
    return SimpleTemplateResponse('ingest/shp.html', context=context)