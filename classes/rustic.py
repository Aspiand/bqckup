from pathlib import Path
from pprint import pprint
import json
import os
import subprocess

from classes.yml_parser import Yml_Parser


class Rustic:
    def __init__(self):
        self.subprocess_args = {
            "capture_output": True,
            "encoding": "utf-8",
            "env": os.environ.copy() | {"RUSTIC_NO_PROGRESS": "true"}, # https://github.com/rustic-rs/rustic/tree/main/config
        }

    def backup(
        self, dirs: list[str], symlink: bool = False, exclude_paths: list[str] = []
    ) -> dict[str, int]:
        dirs = [
            dir
            for dir in dirs
            if Path(dir).exists() or (not symlink and Path(dir).is_symlink())
        ]

        output = subprocess.run(
            [
                "rustic",
                "backup",
                "--json",
                "--git-ignore",
                "--no-scan",
                "--one-file-system",
                *dirs,
            ],
            **self.subprocess_args,
        )

        summary: dict = json.loads(output.stdout)["summary"]

        return {
            "new": summary["files_new"],
            "changed": summary["files_changed"],
            "unchanged": summary["files_unmodified"],
            "total_duration": int(summary["total_duration"]),  # in seconds
        }


def run():
    site_config = Yml_Parser.parse("/etc/bqckup/sites/domain.yml")["bqckup"]
    # storage_config = Yml_Parser.parse("/etc/bqckup/config/storages.yml")
    rustic = Rustic()

    out = rustic.backup(site_config["path"])
    pprint(out)

    # var = subprocess.run(["rustic", "repoinfo", "--json"], env=environment)
    # pprint(var)


# Storage().get_storage_detail(backup.get("options").get("storage")) -> get_primary_storage

# TODO
# check connection
# check repository available
# exclude direct to rustic command
# get_latest backup

# rustic exclude -> --glob="!pattern*"

# Clean
# remove /main.py
