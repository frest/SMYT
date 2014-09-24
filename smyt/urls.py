from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'smyt.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^dynamic/', include('dynamic_models.urls', namespace='dynamic')),
    url(r'^$', RedirectView.as_view(pattern_name='dynamic:index')),
)
