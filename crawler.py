import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import hashlib


class MemeCrawler:
    def __init__(self, base_url="https://mempack.ru/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Создаем папку для сохранения мемов
        self.download_dir = "mempack_memes"
        os.makedirs(self.download_dir, exist_ok=True)

    def get_page_content(self, url):
        """Получает содержимое страницы"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return None

    def extract_links(self, html, current_url):
        """Извлекает все ссылки со страницы"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)

            # Фильтруем только ссылки на том же домене
            if self.is_same_domain(full_url):
                links.append(full_url)

        return links

    def is_same_domain(self, url):
        """Проверяет, принадлежит ли URL тому же домену"""
        parsed_url = urlparse(url)
        parsed_base = urlparse(self.base_url)
        return parsed_url.netloc == parsed_base.netloc

    def extract_images(self, html, page_url):
        """Извлекает изображения со страницы"""
        soup = BeautifulSoup(html, 'html.parser')
        images = []

        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue

            # Получаем полный URL изображения
            img_url = urljoin(page_url, src)

            # Проверяем, что это изображение (по расширению)
            if self.is_image_url(img_url):
                images.append(img_url)

        return images

    def is_image_url(self, url):
        """Проверяет, является ли URL изображением"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        return any(path.endswith(ext) for ext in image_extensions)

    def download_image(self, img_url):
        """Скачивает изображение и сохраняет его"""
        try:
            response = self.session.get(img_url, timeout=10)
            response.raise_for_status()

            # Генерируем имя файла на основе URL
            file_hash = hashlib.md5(img_url.encode()).hexdigest()[:10]
            parsed_url = urlparse(img_url)
            file_ext = os.path.splitext(parsed_url.path)[1]

            if not file_ext:
                # Если расширение не найдено, определяем по content-type
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    file_ext = '.jpg'
                elif 'png' in content_type:
                    file_ext = '.png'
                elif 'gif' in content_type:
                    file_ext = '.gif'
                else:
                    file_ext = '.jpg'  # по умолчанию

            filename = f"meme_{file_hash}{file_ext}"
            filepath = os.path.join(self.download_dir, filename)

            # Сохраняем файл
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"Скачан: {filename}")
            return True

        except Exception as e:
            print(f"Ошибка при скачивании {img_url}: {e}")
            return False

    def crawl(self, start_url=None, max_pages=50):
        """Основной метод для обхода сайта"""
        if start_url is None:
            start_url = self.base_url

        urls_to_visit = [start_url]
        downloaded_images = set()

        while urls_to_visit and len(self.visited_urls) < max_pages:
            current_url = urls_to_visit.pop(0)

            if current_url in self.visited_urls:
                continue

            print(f"Обрабатывается: {current_url}")

            # Получаем содержимое страницы
            html = self.get_page_content(current_url)
            if not html:
                continue

            self.visited_urls.add(current_url)

            # Извлекаем и скачиваем изображения
            images = self.extract_images(html, current_url)
            for img_url in images:
                if img_url not in downloaded_images:
                    if self.download_image(img_url):
                        downloaded_images.add(img_url)

            # Извлекаем ссылки для дальнейшего обхода
            if len(self.visited_urls) < max_pages:
                new_links = self.extract_links(html, current_url)
                for link in new_links:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)

            # Пауза между запросами
            time.sleep(1)

            print(f"Обработано страниц: {len(self.visited_urls)}, Скачано изображений: {len(downloaded_images)}")

        print(
            f"\nЗавершено! Обработано страниц: {len(self.visited_urls)}, Скачано изображений: {len(downloaded_images)}")
        return downloaded_images


def main():
    crawler = MemeCrawler()

    print("Запуск краулера для сайта mempack.ru...")
    print(f"Изображения будут сохранены в папку: {crawler.download_dir}")

    try:
        images = crawler.crawl(max_pages=50)
        print(f"\nУспешно скачано {len(images)} изображений!")

    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()