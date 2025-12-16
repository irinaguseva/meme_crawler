#!/usr/bin/env python3
"""
Главный файл для запуска краулера mempack.ru
"""

import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from crawler.meme_crawler import MemeCrawler
from crawler.exceptions import CrawlerException


def parse_arguments():
    """
    Парсинг аргументов командной строки.
    """
    parser = argparse.ArgumentParser(
        description='Meme Crawler - система для сбора мемов с сайта mempack.ru',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-p', '--pages',
        type=int,
        default=50,
        dest='max_pages',
        help='Максимальное количество страниц для обхода (по умолчанию: 50)'
    )

    return parser.parse_args()

def main():
    print("🎭 MemPack Crawler")
    print("=" * 50)

    try:
        args = parse_arguments()
        max_pages = args.max_pages

        crawler = MemeCrawler()

        print(f"🎯 Целевой сайт: {crawler.base_url}")
        print(f"💾 Папка для сохранения: {crawler.download_dir}")
        print("🔄 Запуск обхода...\n")

        images = crawler.crawl(max_pages=max_pages)

        stats = crawler.get_stats()

        print("\n" + "=" * 50)
        print("✅ ОБХОД ЗАВЕРШЕН!")
        print("=" * 50)
        print(f"📊 СТАТИСТИКА:")
        print(f"   • Обработано страниц: {stats.total_pages}")
        print(f"   • Найдено изображений: {stats.total_images}")
        print(f"   • Успешно скачано: {stats.successful_downloads}")
        print(f"   • Ошибок загрузки: {stats.failed_downloads}")
        print(f"   • Процент успеха: {stats.success_rate:.1f}%")
        print(f"   • Время выполнения: {stats.duration:.2f} сек.")
        print(f"   • Папка с мемами: {crawler.download_dir}")

    except CrawlerException as e:
        print(f"❌ Ошибка краулера: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Обход прерван пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()