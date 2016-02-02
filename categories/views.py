from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.cache import cache

import requests

""" View for bad API requests """
def error(request, status):
	return render(request, 'categories/error.html', {'status': status})

""" User must select this number of categories from the index page """
REQUIRED_NUM_CATEGORIES = 3

""" Index view. Sends request to Eventbrite API for list of categories. This request's JSON response
is cached for 30 minutes """
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

# TODO: sort by date, maybe try to show events' times in user's timezone?

""" Events view. Cached in urls.py. Sends request to Eventbrite API for the HTTP request's
desired list of categories and page number. If no page number, the Eventbrite API defaults to page 1.
Sends response (list of events), categories requested, page number requested, and total number of pages
to template """ 
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
	curPage = pagination['page_number']
	error = ''
	if len(events) == 0:
		error = 'No events found. Try choosing different categories!'
	return render(request, 'categories/events.html', {
		'categories': categories,
		'error': error,
		'events': events,
		'curPage': curPage,
		'pageCount': pagination['page_count']
	})
