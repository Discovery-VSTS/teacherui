from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'index/$', views.index),
    url(r'100-point/$', views.tab_100_points),
    url(r'effort-analysis', views.tab_effort_analysis),
    url(r'team-projects', views.tab_team_projects),
]
