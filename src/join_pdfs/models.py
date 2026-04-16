"""Data models for join-pdfs."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OrganizationFiles:
    """Collection of files belonging to an organization."""

    id: int
    name: str
    base_file: Path
    child_files: list[Path]

    @property
    def all_files(self) -> list[Path]:
        """All files for this organization."""
        return [self.base_file] + self.child_files
