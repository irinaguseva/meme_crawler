import pytest
import requests
import os
from unittest.mock import Mock, patch
from src.crawler.meme_crawler import MemeCrawler
from src.crawler.exceptions import NetworkException, ParsingException


# 12. Юнит-тесты (0.75)

class TestMemeCrawler:

    def setup_method(self):
        self.crawler = MemeCrawler("https://mempack.ru/")

    def test_initialization(self):
        assert self.crawler.base_url == "https://mempack.ru/"
        assert self.crawler.download_dir == "mempack_memes"
        assert os.path.exists(self.crawler.download_dir)

    def test_is_image_url(self):
        valid_urls = [
            "https://mempack.ru/image.jpg",
            "https://mempack.ru/photo.png",
            "https://mempack.ru/meme.gif"
        ]

        invalid_urls = [
            "https://mempack.ru/page.html",
            "https://mempack.ru/script.js"
        ]

        for url in valid_urls:
            assert self.crawler._is_image_url(url) == True

        for url in invalid_urls:
            assert self.crawler._is_image_url(url) == False

    def test_is_excluded_url(self):
        excluded_urls = [
            "https://mempack.ru/logout",
            "https://mempack.ru/auth/login"
        ]

        included_urls = [
            "https://mempack.ru/memes",
            "https://mempack.ru/categories"
        ]

        for url in excluded_urls:
            assert self.crawler._is_excluded_url(url) == True

        for url in included_urls:
            assert self.crawler._is_excluded_url(url) == False

    @patch('requests.Session.get')
    def test_get_page_content_success(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<html>Test content</html>"
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        content = self.crawler.get_page_content("https://mempack.ru/test")

        assert content == "<html>Test content</html>"
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_get_page_content_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(NetworkException):
            self.crawler.get_page_content("https://mempack.ru/test")