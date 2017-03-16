from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'$', views.tab_100_points),
    url(r'login/$', views.login),
    url(r'index/$', views.index),
    url(r'100-point/$', views.tab_100_points),
    url(r'codemetrics/$', views.tab_codemetrics),
]
