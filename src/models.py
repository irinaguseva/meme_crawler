from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from datetime import datetime


# 11. Синтаксический сахар - dataclasses

@dataclass
class ImageInfo:
    url: str
    filename: str
    filepath: Path
    size: Optional[int] = None
    downloaded_at: Optional[datetime] = None

    def __post_init__(self):
        if self.downloaded_at is None:
            self.downloaded_at = datetime.now()

    # 8. Перегрузка операторов (0.5)
    def __str__(self) -> str:
        return f"Image({self.filename}, {self.url})"

    def __repr__(self) -> str:
        return f"ImageInfo(url={self.url!r}, filename={self.filename!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ImageInfo):
            return False
        return self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)

    def __lt__(self, other) -> bool:
        if not isinstance(other, ImageInfo):
            return NotImplemented
        return (self.size or 0) < (other.size or 0)


@dataclass
class CrawlStats:
    total_pages: int = 0
    total_images: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        if self.total_images == 0:
            return 0.0
        return (self.successful_downloads / self.total_images) * 100

    def __add__(self, other):
        if not isinstance(other, CrawlStats):
            return NotImplemented
        return CrawlStats(
            total_pages=self.total_pages + other.total_pages,
            total_images=self.total_images + other.total_images,
            successful_downloads=self.successful_downloads + other.successful_downloads,
            failed_downloads=self.failed_downloads + other.failed_downloads
        )