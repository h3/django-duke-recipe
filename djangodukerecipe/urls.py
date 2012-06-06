from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
   #(r'^i18n/',      include('django.conf.urls.i18n')),
   #(r'^grappelli/', include('grappelli.urls')),
   #(r'',            include('website.urls')),
   #(r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {
   #    'url': '%%swebsite/img/favicon.ico' %% settings.STATIC_URL}),
)

if settings.DEV:
    urlpatterns += patterns('', 
        (r'^%%s(.*)$' %% settings.MEDIA_URL[1:], 
        'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),)
