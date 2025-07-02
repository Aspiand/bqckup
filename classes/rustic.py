from pathlib import Path
from pprint import pprint
import json
import os
import subprocess

from classes.yml_parser import Yml_Parser


class Rustic:
    SUBPROCESS_ARGS = os.environ.copy() | {
        "capture_output": True,
        "text": True,
        "env": os.environ.copy()
        | {
            "RUSTIC_NO_PROGRESS": "true"
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
# handle error

# rustic exclude -> --glob="!pattern*"

# Clean
# remove /main.py
