from django.http import HttpResponse
import datetime

# this is the hello page
def hello(request):
	return HttpResponse("Hello motherfucking big World")
def current_datetime(request):
	now = datetime.datetime.now()
	html = "<html><body>It is now %s.</body></html>" % now
	return HttpResponse(html)
