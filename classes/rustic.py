from pathlib import Path
from typing import Any
from pprint import pprint  # TODO: remove this
from subprocess import CompletedProcess
import json
import toml
import subprocess

from constant import RUSTIC_CONFIG_PATH


class RusticConfigError(Exception): ...


class RusticError(Exception): ...


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
        self.__subprocess_args = {
            "capture_output": True,
            "text": True,
            "check": True,
        }
        self.check_config()
        self.dump_config()

    def backup(self, sources: list[str]) -> dict[str, int]:
        """Running Backup

        Args:
            sources (list[str]): additional locations to backup

        Raises:
            RusticError: rustic return code not 0
        """

        output: CompletedProcess = subprocess.run(
            ["rustic", "backup", "--use-profile", self.site_config["name"], sources],
            **self.__subprocess_args,
        )

        if output.returncode != 0:
            raise RusticError(output.stderr)

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

        rustic_config: dict | None = self.site_config.get("rustic")

        # If rustic field not found
        if rustic_config is None:
            raise RusticConfigError("Rustic not configured")

        if rustic_config.get("password") is None:
            raise RusticConfigError("Password can't be empty")

        if rustic_config.get("config_path"):
            ...  # TODO: handle this?
            # if set; use this instead default path

    def dump_config(self) -> Path:
        """Generate rustic config parsed from storage and site config"""

        config = {  # https://github.com/rustic-rs/rustic/tree/main/config
            "global": {
                # "check-index": True,
                "no-progress": True,
                "log-level": "info",
                # "use-profiles": [self.site_config["name"]],
            },
            "repository": {
                "repository": "opendal:s3",
                "password": self.site_config["rustic"]["password"],
                "options": {
                    "access_key_id": self.storage_config["access_key_id"],
                    "secret_access_key": self.storage_config["secret_access_key"],
                    "region": self.storage_config["region"],
                    "bucket": self.storage_config["bucket"],
                    "endpoint": self.storage_config["endpoint"],
                    "root": f"/ip/{self.site_config['name']}/incremental",
                },
            },
            "backup": {
                "init": True,  # Create repository if not exists
                "json": True,  # Output in json
                "no-scan": True,
                "git-ignore": True,
                "one-file-system": True,
                "snapshots": [{"sources": self.site_config["path"]}],
                "globs": [
                    f"!{i}" for i in self.site_config["exclude_path"]
                ],  # !/tmp/dir1 # see https://github.com/rustic-rs/rustic/discussions/1194#discussioncomment-10298116
            },
            "forget": {"keep-daily": int(self.site_config["options"]["retention"])},
        }

        config_path: Path = Path(RUSTIC_CONFIG_PATH)
        if not config_path.is_dir():  # if not exists
            config_path.mkdir(mode=500)

        with open(config_path / (self.site_config["name"] + ".toml"), "w") as f:
            toml.dump(config, f)

        return config_path


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

# rustic -P aspian -> use config from /etc/rustic with file name aspian.toml
