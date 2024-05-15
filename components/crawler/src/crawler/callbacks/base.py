from typing import Any
from httpx import Response


class CallBack:
    def after_response(self, response: Response) -> Any: ...
