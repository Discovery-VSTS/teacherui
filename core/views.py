from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


def login(request):
    template = get_template('login/login.html')
    return HttpResponse(template.render())

liveStatus = dict(
    navStatus={
        "hundredPt": "",
        "codemetrics": ""
    }
)

def tab_100_points(request):
    template = get_template('tabs/tab_100_points.html')
    liveStatus['navStatus']['hundredPt'] = "active"
    liveStatus['navStatus']['codemetrics'] = ""
    return HttpResponse(template.render(Context(liveStatus)))


def tab_codemetrics(request):
    template = get_template('tabs/tab_codemetrics.html')
    liveStatus['navStatus']['hundredPt'] = ""
    liveStatus['navStatus']['codemetrics'] = "active"
    return HttpResponse(template.render(Context(liveStatus)))

