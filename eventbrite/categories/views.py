from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import requests
# Create your views here.
def error(request, status):
	return render(request, 'categories/error.html', {'status': status})

def index(request):
	# TODO: error messages, check that user only chooses 3 events
	try: 
		response = requests.get(
			'https://www.eventbriteapi.com/v3/categories/',
			headers = {
				'Authorization': 'Bearer 56UBOZLZ4CLCT7JWUQ76'
			},
			verify = True
		)
		response.raise_for_status()
	except requests.exceptions.HTTPError:
		return HttpResponseRedirect(reverse('categories:error', args=(response.status_code,)))			
	return render(request, 'categories/index.html', {'categories': response.json()['categories']})

PAGINATION_LIMIT = 5

def events(request):
	parameters = {}
	categories = []
	if 'category' in request.GET:
		categories = request.GET['category']
		parameters['categories'] = categories
	# TODO: sort by date, maybe try to show events' times in user's timezone?
	# TODO: cache pages
	if 'page' in request.GET:
		parameters['page'] = request.GET['page']
	try:
		response = requests.get(
			'https://www.eventbriteapi.com/v3/events/search/',
			params = parameters,
			headers = {
				'Authorization': 'Bearer 56UBOZLZ4CLCT7JWUQ76'		
			},
			verify = True
		)	
		response.raise_for_status()
	except requests.exceptions.HTTPError:
		return HttpResponseRedirect(reverse('categories:error', args=(response.status_code,)))	
	responseJSON = response.json()
	pagination, events = responseJSON['pagination'], responseJSON['events']
	prevPage, nextPage = -1, -1
	curPage = pagination['page_number']
	firstPageDisplay = max(PAGINATION_LIMIT * ((curPage - 1) // PAGINATION_LIMIT) + 1, 1)
	lastPageDisplay = min(firstPageDisplay + PAGINATION_LIMIT - 1, pagination['page_count'])
	if firstPageDisplay != 1:
		prevPage = firstPageDisplay - 1
	if lastPageDisplay < pagination['page_count']:
		nextPage = lastPageDisplay + 1
	error = ''
	if len(events) == 0:
		error = 'No events found. Try choosing different categories!'
	return render(request, 'categories/events.html', {
		'categories': categories,
		'error': error,
		'events': events,
		'curPage': curPage,
		'prevPage': prevPage,
		'nextPage': nextPage,
		'pageDisplays': range(firstPageDisplay, lastPageDisplay + 1)
	})
