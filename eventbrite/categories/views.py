from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import requests
# Create your views here.
def index(request):
	# TODO: check for errors in request
	# TODO: error messages, check that user only chooses 3 events
	response = requests.get(
		'https://www.eventbriteapi.com/v3/categories/',
		headers = {
			'Authorization': 'Bearer 56UBOZLZ4CLCT7JWUQ76'
		},
		verify = True
	)
	return render(request, 'categories/index.html', {'categories': response.json()['categories']})

def events(request):
	if 'category' not in request.GET:
		return HttpResponseRedirect(reverse('categories:index'))
	# TODO: sort by date, maybe try to show events' times in user's timezone?
	# TODO: pagination
	response = requests.get(
		'https://www.eventbriteapi.com/v3/events/search/',
		params = {
			'categories': request.GET['category']
		},
		headers = {
			'Authorization': 'Bearer 56UBOZLZ4CLCT7JWUQ76'		
		},
		verify = True
	)
	return render(request, 'categories/events.html', {'events': response.json()['events']})