import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

backend_url = os.getenv("backend_url", "http://127.0.0.1:3030").strip().rstrip("/")
sentiment_analyzer_url = os.getenv("sentiment_analyzer_url", "").strip().rstrip("/")


def get_request(endpoint, **kwargs):
    request_url = backend_url + "/" + endpoint.lstrip("/")
    print(f"GET from {request_url}")
    response = requests.get(request_url, params=kwargs, timeout=20)
    response.raise_for_status()
    return response.json()


def analyze_review_sentiments(text):
    if not sentiment_analyzer_url:
        raise ValueError("Set sentiment_analyzer_url in djangoapp/.env")
    request_url = sentiment_analyzer_url + "/analyze/" + quote(text, safe="")
    response = requests.get(request_url, timeout=30)
    response.raise_for_status()
    return response.json()


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    response = requests.post(request_url, json=data_dict, timeout=20)
    response.raise_for_status()
    return response.json()
