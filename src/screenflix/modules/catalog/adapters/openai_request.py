import os

from screenflix.core.settings import get_settings
from screenflix.modules.catalog.adapters.base_http_request import BaseHttpRequest


class OpenAIRequest(BaseHttpRequest):

    def __init__(self):
        settings = get_settings()
        headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
        super().__init__(base_url=settings.openai_api_url, headers=headers)