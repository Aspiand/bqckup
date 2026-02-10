from dataclasses import dataclass
from typing import List, Dict, Any

from helpers.utility import now

@dataclass
class BackupJob:
    success: bool
    size: int
    errors: List[Any]
    started_at: int
    ended_at: int
    metadata: Dict[str, Any]

    def start(self):
        self.started_at = now()
        return self

    # def fail(self, traceback: str):
    #     self.status = 'failed'
    #     self.ended_at = now()
    #     return self

    def complete(self):
        self.success = True
        self.ended_at = now()