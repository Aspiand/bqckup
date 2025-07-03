from pathlib import Path
from typing import Any
from pprint import pprint # TODO: remove this
import json
import os
import subprocess

from constant import RUSTIC_CONFIG_PATH


class RusticConfigError(Exception): ...


class Rustic:
    def __init__(self, site_config: dict[str, Any], storage_config: dict[str, Any]):
        # self.__SUBPROCESS_ARGS = {
        #     "capture_output": True,
        #     "text": True,
        #     "env": os.environ.copy()
        #     | {
        #         "RUSTIC_NO_PROGRESS": "true",
        #         "RUSTIC_LOG_LEVEL": "info",
        #         # "RUSTIC_REPOSITORY": "opendal:S3",
        #     },
        #     # https://github.com/rustic-rs/rustic/tree/main/config
        #     # https://github.com/langgenius/dify/issues/12200
        # }

        # Site Config:
        #     name: domain
        #     enabled: no
        #     path:
        #         - /var/www/html
        #     exclude_path:
        #         - cache
        #     database:
        #         type: mysql
        #         host: localhost
        #         port: 3306
        #         user: root
        #         password: root
        #         name: database
        #     options:
        #         storage: dummy
        #         interval: daily # can be daily, weekly, monthly 
        #         retention: '7'
        #         follow_symlink: no
        #         save_locally: no
        #         save_locally_path: /etc/bqckup/tmp
        #         notification_email: email@example.com
        #         provider: s3

        # # Selected by options on Site Config
        # Storage Config:
        #     bucket: dummy
        #     access_key_id: dummy
        #     secret_access_key: dummy
        #     region: dummy
        #     endpoint: dummy
        #     primary: no

        self.site_config = site_config
        self.storage_config = storage_config[site_config["options"]["storage"]]
        self.check_config()

    def backup(
        self, sources: list[str], symlink: bool = False, exclude_paths: list[str] = []
    ) -> dict[str, int]:
        raise RuntimeError("not avaiable for now")
        sources = [
            src
            for src in sources
            if Path(src).exists() and not (not symlink and Path(src).is_symlink())
        ]

        output = subprocess.run(
            [
                "rustic",
                "backup",
                "--json",
                # "--git-ignore",
                "--no-scan",
                "--one-file-system",
                # Create repository if not exists
                "--init",
                *sources,
            ],
            **self.__SUBPROCESS_ARGS,
        )

        summary: dict = json.loads(output.stdout)["summary"]

        return {
            "new": summary["files_new"],
            "changed": summary["files_changed"],
            "unchanged": summary["files_unmodified"],
            "total_duration": int(summary["total_duration"]),  # in seconds
            "uploaded": summary[
                "data_added_packed"
            ],  # data added to repository (compressed); in byte
            "total_size": summary["total_bytes_processed"],
        }

    def check_config(self):
        """Check rustic configuration from sites

        Raises:
            RusticConfigError: rustic not configured
            RusticConfigError: password empty
        """

        rustic_config = self.site_config.get("rustic")

        # If rustic field not found
        if rustic_config is None:
            raise RusticConfigError("field not found")

        if rustic_config.get("password") is None:
            raise RusticConfigError("password empty")

        if rustic_config.get("config_path"):
            ...  # TODO: handle this?
            # if set; use this instead default path

    def dump_config(self, path: str = None) -> str:
        """Generate rustic config parsed from storage and site config"""

        # use library?
        content = f"""# GENERATED FILE. DON'T CHANGE THIS!.
[repository]
repository = "opendal:s3"
password = "{self.site_config["rustic"]["password"]}"

[repository.options]
access_key_id = "{self.storage_config["access_key_id"]}"
secret_access_key = "{self.storage_config["secret_access_key"]}"
region = "{self.storage_config["region"]}"
bucket = "{self.storage_config["bucket"]}"
endpoint = "{self.storage_config["endpoint"]}"
root = "/ip/{self.site_config["name"]}/incremental"

[backup]
json = true

[[backup.snapshots]]
sources = [""] # TODO: later

[forget]
keep-daily={self.site_config["options"]["retention"]}
"""
        config_path = (
            path
            if path
            else (Path(RUSTIC_CONFIG_PATH) / self.site_config["name"]).with_suffix(
                ".toml"
            )
        )

        pprint(content)
        # with open(config_path, "w") as f:
        #     f.writelines(content)

    # Membuat file konfigurasi rustic berdasarkan dari storage.yml dan domain.yml' jika tidak menggunakan environment variable


# Storage().get_storage_detail(backup.get("options").get("storage")) -> get_primary_storage

# TODO
# check connection
# check repository available
# exclude direct to rustic command
# get_latest backup
# keep n
# handle error
# handle error pada scoope paling tinggi (run) -> log
# key subcommand # Important
# check repository avaibility

# secrets -> env???
# - delete secrets from rustic config
# - define aws env variable
# - test

# rustic exclude -> --glob="!pattern*"

# NOTE
# from playhouse.shortcuts import model_to_dict
# REPOSITORY -> $ROOT/domain/incremental

# https://github.com/langgenius/dify/issues/12200
# OPENDAL_S3_ENDPOINT
# OPENDAL_S3_REGION
# OPENDAL_S3_BUCKET
# OPENDAL_S3_ACCESS_KEY_ID
# OPENDAL_S3_SECRET_ACCESS_KEY

# ❯ rustic --use-profile ~/.config/rustic/aspian repoinfo
# [INFO] using config /home/pc/.config/rustic/aspian.toml
