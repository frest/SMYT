from django.conf.urls import url, patterns

from . import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^table/(?P<model>[\w]+)/$',
        views.ModelListView.as_view(), name='table'),

    url(r'^create/(?P<model>[\w]+)/$',
        views.ModelCreateView.as_view(), name='create'),

    url(r'^delete/(?P<model>[\w]+)/(?P<pk>[\d]+)/$',
        views.ModelDeleteView.as_view(), name='delete'),

    url(r'^update/(?P<model>[\w]+)/(?P<pk>[\d]+)/$',
        views.ModelUpdateView.as_view(), name='update'),
)
