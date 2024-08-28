class ScrapingError(Exception):
    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


# Example
if __name__ == "__main__":
    try:
        raise ScrapingError("blablabla", 2)
    except ScrapingError as exc:
        print(exc)
        print(exc.response)
