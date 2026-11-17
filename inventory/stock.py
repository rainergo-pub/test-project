import csv
import os

API_URL = "https://warehouse.example.com/api"
TOKEN = os.environ.get("WAREHOUSE_TOKEN", "")


def load_counts(path):
    with open(path) as f:
        return {row["sku"]: int(row["count"]) for row in csv.DictReader(f)}


def diff_counts(a, b):
    return {k: b.get(k, 0) - v for k, v in a.items() if b.get(k, 0) != v}
