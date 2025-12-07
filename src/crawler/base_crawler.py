from abc import ABC, abstractmethod
from typing import List, Set
import requests
from bs4 import BeautifulSoup
import time

from src.decorators import retry, timing
from src.models import CrawlStats, ImageInfo
from src.crawler.exceptions import NetworkException, ParsingException


# 4. Использование абстрактных классов (0.5)
class BaseCrawler(ABC):

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.stats = CrawlStats()
        self._setup_session()

    def _setup_session(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        })

    @abstractmethod
    def extract_links(self, html: str, current_url: str) -> List[str]:
        pass

    @abstractmethod
    def extract_images(self, html: str, page_url: str) -> List[str]:
        pass

    @retry(max_attempts=3, delay=1.0)
    def get_page_content(self, url: str) -> str:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            raise NetworkException(f"Ошибка сети для {url}: {e}")

    @timing
    def crawl(self, start_url: str = None, max_pages: int = 50) -> Set[ImageInfo]:
        if start_url is None:
            start_url = self.base_url

        self.stats.start_time = time.time()
        downloaded_images = self._perform_crawl(start_url, max_pages)
        self.stats.end_time = time.time()

        return downloaded_images

    def _perform_crawl(self, start_url: str, max_pages: int) -> Set[ImageInfo]:
        visited_urls = set()
        urls_to_visit = [start_url]
        downloaded_images = set()

        while urls_to_visit and len(visited_urls) < max_pages:
            current_url = urls_to_visit.pop(0)

            if current_url in visited_urls:
                continue

            print(f"📄 Обрабатывается [{len(visited_urls) + 1}/{max_pages}]: {current_url}")

            html = self.get_page_content(current_url)
            if not html:
                visited_urls.add(current_url)
                continue

            visited_urls.add(current_url)
            self.stats.total_pages += 1

            images = self._process_images(html, current_url, downloaded_images)
            downloaded_images.update(images)

            if len(visited_urls) < max_pages:
                new_links = self.extract_links(html, current_url)
                for link in new_links:
                    if link not in visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)

            time.sleep(1)

        return downloaded_images

    def _process_images(self, html: str, page_url: str, downloaded_images: Set[ImageInfo]) -> Set[ImageInfo]:
        image_urls = self.extract_images(html, page_url)
        new_images = set()

        for img_url in image_urls:
            if any(img.url == img_url for img in downloaded_images):
                continue

            image_info = self.download_image(img_url)
            if image_info:
                new_images.add(image_info)
                self.stats.successful_downloads += 1
            else:
                self.stats.failed_downloads += 1
            self.stats.total_images += 1

            time.sleep(0.5)

        return new_images

    @abstractmethod
    def download_image(self, img_url: str) -> ImageInfo:
        pass

    def get_stats(self) -> CrawlStats:
        return self.stats