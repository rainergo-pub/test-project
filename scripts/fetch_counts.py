import requests

from inventory.stock import API_URL, TOKEN

resp = requests.get(API_URL + "/counts", headers={"Authorization": TOKEN})
open("counts.csv", "w").write(resp.text)
