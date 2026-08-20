import httpx


BASE_URL = "http://localhost:8001"
api_client = httpx.AsyncClient(base_url=BASE_URL)


class ApiError(Exception):
    """Raised when an error occurs while making a request to the API"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


class ApiClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self._client = httpx.AsyncClient(base_url=self.base_url)

    @staticmethod
    async def _handle(response: httpx.Response):
        """Centralized error handling so callers don't repeat status checks"""
        if response.is_error:
            raise ApiError(response.status_code, response.text)
        return response.json()

    async def get(self, path: str, params: dict | None = None) -> dict:
        response = await self._client.get(path, params=params)
        return await self._handle(response)

    async def post(self, path: str, json: dict | None = None) -> dict:
        response = await self._client.post(path, json=json)
        return await self._handle(response)

api = ApiClient()
