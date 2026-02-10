from dataclasses import dataclass
from typing import List, Dict

from classes.dataclass import BackupJob

@dataclass
class BackupContext:
    started_at: int
    ended_at: int
    config: Dict
    file: BackupJob
    databases: List[BackupJob]
