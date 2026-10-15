# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review
import requests


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
    try:
        data = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    username = data.get("userName", "").strip()
    password = data.get("password", "")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    email = data.get("email", "").strip()
    if not username or not password:
        return JsonResponse({"error": "Username and password are required"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"userName": username, "error": "Already Registered"})
    user = User.objects.create_user(username=username, password=password,
                                    first_name=first_name, last_name=last_name, email=email)
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...


def get_cars(request):
    if not CarMake.objects.exists():
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name}
            for car_model in car_models]
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else "/fetchDealers/" + state
    try:
        dealerships = get_request(endpoint)
        return JsonResponse({"status": 200, "dealers": dealerships})
    except (requests.RequestException, ValueError) as error:
        logger.error("Unable to fetch dealerships: %s", error)
        return JsonResponse({"status": 502, "message": "Unable to fetch dealerships"}, status=502)


def get_dealer_details(request, dealer_id):
    try:
        dealership = get_request("/fetchDealer/" + str(dealer_id))
        return JsonResponse({"status": 200, "dealer": dealership})
    except (requests.RequestException, ValueError) as error:
        logger.error("Unable to fetch dealer: %s", error)
        return JsonResponse({"status": 502, "message": "Unable to fetch dealer"}, status=502)


def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request("/fetchReviews/dealer/" + str(dealer_id))
    except (requests.RequestException, ValueError) as error:
        logger.error("Unable to fetch reviews: %s", error)
        return JsonResponse({"status": 502, "message": "Unable to fetch reviews"}, status=502)
    for review_detail in reviews:
        try:
            response = analyze_review_sentiments(review_detail.get("review", ""))
            review_detail["sentiment"] = response["sentiment"]
        except (requests.RequestException, ValueError, KeyError) as error:
            logger.error("Unable to analyze review sentiment: %s", error)
            return JsonResponse({"status": 502, "message": "Sentiment analyzer unavailable"}, status=502)
    return JsonResponse({"status": 200, "reviews": reviews})


@csrf_exempt
def add_review(request):
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"}, status=403)
    if request.method != "POST":
        return JsonResponse({"status": 405, "message": "Method Not Allowed"}, status=405)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError("Review data must be an object")
        post_review(data)
        return JsonResponse({"status": 200})
    except (ValueError, TypeError):
        return JsonResponse({"status": 400, "message": "Invalid review data"}, status=400)
    except requests.RequestException as error:
        logger.error("Error posting review: %s", error)
        return JsonResponse({"status": 502, "message": "Error in posting review"}, status=502)
