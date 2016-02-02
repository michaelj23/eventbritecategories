from django.conf.urls import url
from django.views.decorators.cache import cache_page
from . import views

app_name = 'categories'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^events', cache_page(60 * 5)(views.events), name='events'),
	url(r'^error/(?P<status>[0-9]+)', cache_page(60 * 60)(views.error), name='error')
]