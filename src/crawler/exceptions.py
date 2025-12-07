# 9. Использование каких-либо исключений (0.25)
# 10. Использование исключений своего собственного типа (0.25)

class CrawlerException(Exception):
    pass

class NetworkException(CrawlerException):
    pass

class ParsingException(CrawlerException):
    pass

class ImageDownloadException(CrawlerException):
    pass