import os
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from src.crawler.base_crawler import BaseCrawler
from src.decorators import log_execution, retry
from src.models import ImageInfo
from src.utils import URLProcessor
from src.crawler.exceptions import ParsingException, ImageDownloadException


# 2. Использование наследования от какого-нибудь класса (0.5)
# 3. Использование наследования от созданного своими руками класса (0.5)
class MemeCrawler(BaseCrawler):

    def __init__(self, base_url: str = "https://mempack.ru/"):
        super().__init__(base_url)
        self.download_dir = "mempack_memes"
        self.url_processor = URLProcessor()
        self._create_download_dir()

    def _create_download_dir(self):
        os.makedirs(self.download_dir, exist_ok=True)

    @log_execution
    def extract_links(self, html: str, current_url: str) -> List[str]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)

                if (self.url_processor.is_same_domain(full_url, self.base_url) and
                        not self._is_excluded_url(full_url)):
                    links.append(full_url)

            return list(set(links))
        except Exception as e:
            raise ParsingException(f"Ошибка парсинга ссылок: {e}")

    @log_execution
    def extract_images(self, html: str, page_url: str) -> List[str]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            images = []

            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if not src:
                    continue

                img_url = urljoin(page_url, src)
                if self._is_image_url(img_url):
                    images.append(img_url)

            return list(set(images))
        except Exception as e:
            raise ParsingException(f"Ошибка парсинга изображений: {e}")

    def _is_excluded_url(self, url: str) -> bool:
        excluded_patterns = ['logout', 'signout', 'auth', 'login', 'register']
        return any(pattern in url.lower() for pattern in excluded_patterns)

    def _is_image_url(self, url: str) -> bool:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        return any(path.endswith(ext) for ext in image_extensions)

    @retry(max_attempts=2, delay=0.5)
    def download_image(self, img_url: str) -> ImageInfo:
        try:
            response = self.session.get(img_url, timeout=10, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise ImageDownloadException(f"Не изображение: {img_url}")

            filename = self.url_processor.generate_filename(img_url, content_type)
            filepath = os.path.join(self.download_dir, filename)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            size = os.path.getsize(filepath)

            print(f"✅ Скачан: {filename}")
            return ImageInfo(
                url=img_url,
                filename=filename,
                filepath=filepath,
                size=size
            )

        except Exception as e:
            raise ImageDownloadException(f"Ошибка загрузки {img_url}: {e}")