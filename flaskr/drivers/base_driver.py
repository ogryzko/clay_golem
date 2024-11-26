from flaskr.utils.logger import Logger
from typing import Optional

class BaseDriver:
    def __init__(self, host: str, name: str = "unnamed"):
        self.name = name
        self.base_url = f"http://{host}"
        self.logger = Logger.get_logger(f"{self.__class__.__name__}_{self.name}") 