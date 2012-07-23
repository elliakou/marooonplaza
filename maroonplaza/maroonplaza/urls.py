from django.conf.urls import patterns, include, url
from maroonplaza.views import hello, current_datetime

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	('^hello/$', hello),
	#('^event/$', event),
	#('^index/$', index),
	#('^submit/$', submit),
	#('^listevents/$', listevents),
	('^time/$', current_datetime),
)