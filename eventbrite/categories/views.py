from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.cache import cache

import requests
# Create your views here.
def error(request, status):
	return render(request, 'categories/error.html', {'status': status})

REQUIRED_NUM_CATEGORIES = 3

def index(request):
	responseJSON = cache.get('index')
	if not responseJSON:
		try: 
			response = requests.get(
				'https://www.eventbriteapi.com/v3/categories/',
				headers = {
					'Authorization': 'Bearer 56UBOZLZ4CLCT7JWUQ76'
				},
				verify = True
			)
			response.raise_for_status()
			responseJSON = response.json()
			cache.set('index', responseJSON, 60 * 30)
		except requests.exceptions.HTTPError:
			return HttpResponseRedirect(reverse('categories:error', args=(response.status_code,)))			
	return render(request, 'categories/index.html', {'categories': responseJSON['categories']})

PAGINATION_LIMIT = 5

# TODO: sort by date, maybe try to show events' times in user's timezone?

def events(request):
	if 'category' not in request.GET or len(request.GET.getlist('category')) != REQUIRED_NUM_CATEGORIES:
		messages.error(request, 'Please select %d categories.' % REQUIRED_NUM_CATEGORIES)
		return HttpResponseRedirect(reverse('categories:index'))
	categories = request.GET.getlist('category')
	parameters = {
		'categories': categories
	}
	if 'page' in request.GET:
		parameters['page'] = request.GET['page']
	else:
		parameters['page'] = 1 # cache the first page more consistently by making its URL consistent
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
		prevPage = firstPageDisplay - PAGINATION_LIMIT
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
