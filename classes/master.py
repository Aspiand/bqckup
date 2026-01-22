import requests
import traceback
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Dict, Any
from rich import print

from classes.config import Config
from constant import MAX_RETRIES
from constant import VERSION
from helpers.utility import is_debug


class Master:
    __instance = None

    @staticmethod
    def get():
        if Master.__instance is None:
            Master.__instance = Master()
        return Master.__instance

    def __init__(self):
        if Master.__instance is not None:  # return instance?
            raise Exception("This class is a singleton!")

        self.config = Config()
        self.url = self.config.read("master", "url", print_error=False)
        self.api_key = self.config.read("master", "api_key", print_error=False)
        self.enabled = bool(self.url and self.api_key)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"bqckup/{VERSION}",
            }
        )

        # Retry strategy with Exponential Backoff and Jitter
        # - total: total number of retries
        # - backoff_factor: sleep factor (sleep_seconds = backoff_factor * (2 ** (retry_count - 1)))
        # - status_forcelist: HTTP status codes to retry on (5xx errors)
        # - method_whitelist: HTTP methods to retry (POST is generally not idempotent, but here we assume safe)
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,  # Start with 1s, then 2s, 4s, etc.
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def send(self, payload: Dict[str, Any]) -> None:
        if not self.enabled:
            return

        endpoint = f"{self.url.rstrip('/')}/api/v1/backup/new"

        try:
            # We use a custom backoff loop for more control (like Jitter) if needed,
            # but requests.adapters.Retry is cleaner for standard cases.
            # To add Jitter manually we would wrap this in a loop, but for now
            # standard exponential backoff provided by urllib3 is a good minimal start.

            response = self.session.post(endpoint, json=payload, timeout=30)

            if response.status_code == 201 or response.status_code == 204:
                if is_debug():
                    print(f"[green]Successfully sent report to master: {response.status_code}[/green]")
            else:
                print(f"[red]Failed to send report to master. Status: {response.status_code}. Response: {response.text}[/red]")

        except RequestException as e:
            if is_debug():
                traceback.print_exc()
            print(f"[red]Error connecting to master: {e}[/red]")
        except Exception as e:
            if is_debug():
                traceback.print_exc()
            print(f"[red]Unexpected error in Master client: {e}[/red]")
