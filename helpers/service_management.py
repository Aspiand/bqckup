import requests

from classes.config import Config

base_url = Config().read("notification", "service_management_url")


def get_credential(bucket_name: str):
    r = requests.get(f"{base_url}/bqckup/get/{bucket_name}")
    if r.status_code != 200:
        raise requests.RequestException(r)

    return r.json()


def send_backup_summary(): ...
