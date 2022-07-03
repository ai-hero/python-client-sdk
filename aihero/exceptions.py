class AIHeroException(Exception):
    """Generic AI Hero exception class"""

    def __init__(self, message, status_code=None):
        if not message:
            message = type(self).__name__

        self.message = message
        if status_code:
            super().__init__(f"<Response [{status_code}]> {message}")
        else:
            super().__init__(f"{message}")
