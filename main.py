from pathlib import Path

from classes.rustic import Rustic
from classes.yml_parser import Yml_Parser
from constant import SITE_CONFIG_PATH, STORAGE_CONFIG_PATH

if __name__ == "__main__":
    Rustic(
        Yml_Parser.parse((Path(SITE_CONFIG_PATH) / "aspian.my.id").__str__())["bqckup"],
        Yml_Parser.parse(STORAGE_CONFIG_PATH)["storages"]
    )