import pytest
from pathlib import Path
from src.models import ImageInfo, CrawlStats
from datetime import datetime


class TestImageInfo:

    def test_image_info_creation(self):
        image = ImageInfo(
            url="https://example.com/image.jpg",
            filename="test.jpg",
            filepath=Path("/tmp/test.jpg")
        )

        assert image.url == "https://example.com/image.jpg"
        assert image.filename == "test.jpg"
        assert isinstance(image.downloaded_at, datetime)

    def test_image_info_equality(self):
        image1 = ImageInfo("url1", "file1", Path("/tmp/file1"))
        image2 = ImageInfo("url1", "file2", Path("/tmp/file2"))
        image3 = ImageInfo("url2", "file1", Path("/tmp/file1"))

        assert image1 == image2
        assert image1 != image3

    def test_image_info_hash(self):
        image1 = ImageInfo("url1", "file1", Path("/tmp/file1"))
        image2 = ImageInfo("url1", "file2", Path("/tmp/file2"))

        assert hash(image1) == hash(image2)


class TestCrawlStats:

    def test_stats_addition(self):
        stats1 = CrawlStats(
            total_pages=10,
            total_images=20,
            successful_downloads=15,
            failed_downloads=5
        )

        stats2 = CrawlStats(
            total_pages=5,
            total_images=10,
            successful_downloads=8,
            failed_downloads=2
        )

        result = stats1 + stats2

        assert result.total_pages == 15
        assert result.total_images == 30
        assert result.successful_downloads == 23
        assert result.failed_downloads == 7

    def test_success_rate(self):
        stats = CrawlStats(
            total_images=100,
            successful_downloads=75,
            failed_downloads=25
        )

        assert stats.success_rate == 75.0

    def test_success_rate_zero(self):
        stats = CrawlStats()

        assert stats.success_rate == 0.0