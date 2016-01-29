from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import requests
# Create your views here.
def index(request):
	response = requests.get(
		'https://www.eventbriteapi.com/v3/categories/',
		headers = {
			'Authorization': 'Bearer 56UBOZLZ4CLCT7JWUQ76'
		},
		verify = True
	)
	return render(request, 'categories/index.html', {'categories': response.json()['categories']})
	return JsonResponse(response.json())
