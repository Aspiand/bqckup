from pathlib import Path
from pprint import pprint
import os
import subprocess
from typing import Any

from classes.yml_parser import Yml_Parser


class Rustic:
    def __init__(
        self,
        site_config: dict[str, Any],
        storage_config: dict[str, Any] = {},
        env: dict[str, str] = {},
    ):
        self.site_config = site_config
        self.storage_config = storage_config
        self.env = env

    @property
    def directories(self):
        """Return which directory backups"""
        # TODO
        # filter in here or not?
        return [dir for dir in self.site_config["path"] if Path(dir).exists()]

    @property
    def excluded(self):
        return self.site_config["exclude_path"]

    def backup(self, dirs: list[str], exclude: list[str] = []):
        dirs = [
            dir for dir in dirs if Path(dir).exists() and not Path(dir).is_symlink()
        ]
        options = ["--git-ignore", "--one-file-system"]

        self.run("backup", *(options + dirs))

    def snapshots(self):
        return self.run("snapshots")

    def run(self, subcommand: str, options: list[str] = []):
        result = subprocess.run(
            ["rustic", subcommand, *options, "--json"], env=self.env
        )

        pprint(result)

        if result.returncode != 0:
            ...  # TODO: handle this


def run():
    environment = os.environ.copy() | {"RUSTIC_NO_PROGRESS": "true"}

    site_config = Yml_Parser.parse("/etc/bqckup/sites/domain.yml.example")["bqckup"]
    rustic = Rustic(site_config, environment)

    # rustic.snapshots()
    pprint(rustic.excluded)

    # var = subprocess.run(["rustic", "repoinfo", "--json"], env=environment)
    # pprint(var)


# Storage().get_storage_detail(backup.get("options").get("storage")) -> get_primary_storage

# TODO
# check connection
# check repository available
# exclude direct to rustic command
# add label for snapshot name
# get_latest backup

# rustic exclude -> --glob="!pattern*"

# Clean
# remove /main.py
