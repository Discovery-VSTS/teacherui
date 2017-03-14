from django.http import HttpResponse
from django.template.loader import get_template
import datetime


def current_datetime(request):
    html = get_template('base.html')
    return HttpResponse(html.render())
