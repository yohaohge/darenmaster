import requests
from collections import defaultdict
import os
import uuid
import pickle

device = ""
if os.path.exists("user_data/device.pickle"):
    with open("user_data/device.pickle", "rb") as f:
        data = pickle.load(f)
        device = data["device"]
else:
    device = uuid.uuid1()
    data = {
        "device": device
    }
    with open("user_data/device.pickle", "wb") as f:
        pickle.dump(data, f)

print(device)


def login_api(username, password)->bool:
    headers = {
            "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "open_id": username,
        "password": password,
        "uuid": device,
    }
    response = requests.post("http://106.52.44.49:504/api/login", headers=headers, data=data)

    if response.status_code != 200:
        print("code", response.status_code)
        return False

    if response.json()['code'] != 0:
        print(response.json())
        return False

    print(response.json())
    return True

def heart_beat(username, password)->bool:
    headers = {
            "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "open_id": username,
        "password": password,
        "uuid": device,
        "heart_beat":True,
    }
    response = requests.post("http://106.52.44.49:504/api/login", headers=headers, data=data)

    if response.status_code != 200:
        print("code", response.status_code)
        return False

    if response.json()['code'] != 0:
        print(response.json())
        return False

    print(response.json())
    return True