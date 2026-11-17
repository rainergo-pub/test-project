import os
import requests

API_URL = "https://example.com/api"


def fetch(path):
    return requests.get(API_URL + path, timeout=5).json()


def main():
    print("legacy", os.getenv("LEGACY_TOKEN", "none"))
