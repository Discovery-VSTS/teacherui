from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


def login(request):
    template = get_template('login/login.html')
    return HttpResponse(template.render())

liveStatus = dict(navStatus={"100pt": "", "codemetrics": ""})

def index(request):
    html = get_template('tabs/tab_100_points.html')
    liveStatus['navStatus']['100pt'] = "active"
    liveStatus['navStatus']['codemetrics'] = ""
    return HttpResponse(html.render(Context(liveStatus)))


def tab_100_points(request):
    template = get_template('tabs/tab_100_points.html')
    liveStatus['navStatus']['100pt'] = "active"
    liveStatus['navStatus']['codemetrics'] = ""
    return HttpResponse(template.render(Context(liveStatus)))


def tab_codemetrics(request):
    template = get_template('tabs/tab_codemetrics.html')
    liveStatus['navStatus']['100pt'] = ""
    liveStatus['navStatus']['codemetrics'] = "active"
    return HttpResponse(template.render(Context(liveStatus)))

