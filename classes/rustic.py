from pathlib import Path
from pprint import pprint
import json
import os
import subprocess

from classes.yml_parser import Yml_Parser


class Rustic:
    SUBPROCESS_ARGS = {
        "capture_output": True,
        "text": True,
        "env": os.environ.copy()
        | {
            "RUSTIC_NO_PROGRESS": "true",
            "RUSTIC_LOG_LEVEL": "info",
        },  # https://github.com/rustic-rs/rustic/tree/main/config
    }

    @classmethod
    def backup(
        cls, sources: list[str], symlink: bool = False, exclude_paths: list[str] = []
    ) -> dict[str, int]:
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
            **cls.SUBPROCESS_ARGS,
        )

        summary: dict = json.loads(output.stdout)["summary"]

        return {
            "new": summary["files_new"],
            "changed": summary["files_changed"],
            "unchanged": summary["files_unmodified"],
            "total_duration": int(summary["total_duration"]),  # in seconds
            "uploaded": summary["data_added_packed"], # data added to repository (compressed); in byte
            "total_size": summary["total_bytes_processed"],
        }

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
# add label by domain?
# check repository avaibility

# rustic exclude -> --glob="!pattern*"

# Clean
# remove /main.py

# NOTE
# from playhouse.shortcuts import model_to_dict


# https://github.com/langgenius/dify/issues/12200
# OPENDAL_S3_ENDPOINT
# OPENDAL_S3_REGION
# OPENDAL_S3_BUCKET
# OPENDAL_S3_ACCESS_KEY_ID
# OPENDAL_S3_SECRET_ACCESS_KEY