from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'datetime/$', views.current_datetime),
]
