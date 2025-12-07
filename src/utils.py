import hashlib
import os
from urllib.parse import urljoin, urlparse
from pathlib import Path


# 11. Прочий "синтаксический сахар" Питона (0.5)

class URLProcessor:

    @staticmethod
    def normalize_url(url: str, base_url: str) -> str:
        return urljoin(base_url, url)

    @staticmethod
    def is_same_domain(url: str, base_domain: str) -> bool:
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_domain)
        return parsed_url.netloc == parsed_base.netloc

    @staticmethod
    def generate_filename(url: str, content_type: str = "") -> str:
        if file_hash := hashlib.md5(url.encode()).hexdigest()[:10]:
            parsed_url = urlparse(url)
            file_ext = Path(parsed_url.path).suffix.lower()

            match file_ext:
                case '.jpg' | '.jpeg' | '.png' | '.gif' | '.webp' | '.bmp' if file_ext:
                    return f"meme_{file_hash}{file_ext}"
                case _:
                    ext_map = {
                        'image/jpeg': '.jpg',
                        'image/jpg': '.jpg',
                        'image/png': '.png',
                        'image/gif': '.gif',
                        'image/webp': '.webp'
                    }
                    return f"meme_{file_hash}{ext_map.get(content_type, '.jpg')}"
        return f"meme_{hashlib.md5(url.encode()).hexdigest()[:10]}.jpg"