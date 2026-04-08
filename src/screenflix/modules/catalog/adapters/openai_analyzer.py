import json
from typing import Dict, Any

from screenflix.core.logging.logger import get_logger
from screenflix.core.settings import get_settings
from screenflix.core.utils.shortcuts import get_json_schemas
from screenflix.modules.catalog.adapters.base_http_request import BaseHttpRequest

logger = get_logger(__name__)

MEDIA_SYSTEM_PROMPT = """
Você é um assistente de catalogação de mídia.

Sua tarefa é analisar um objeto JSON de entrada e retornar um novo objeto JSON que siga estritamente o schema informado.

Regras obrigatórias:
- Retorne somente JSON válido.
- Não inclua explicações, comentários, markdown ou texto adicional.
- Siga exatamente os nomes dos campos definidos no schema.
- Não invente informações.
- Se um campo não estiver disponível ou for "N/A", use null quando o schema permitir.
- Converta valores para os tipos exigidos pelo schema.
- Datas devem estar no formato YYYY-MM-DD.
- Números devem ser retornados como number, não como string.
- Arrays devem conter apenas strings limpas e normalizadas.
- Se o título original estiver em inglês, traduza o título principal para português e preserve o original em original_title.
- Se o conteúdo for uma série, use media_type = "series".
- Se o conteúdo for um filme, use media_type = "movie".
"""

MEDIA_USER_PROMPT = """
Analise o JSON de entrada e produza um JSON de saída compatível com o schema "media".

Regras de mapeamento:
- title: traga o titulo que foi publicado no brasil.
- original_title: mantenha o título original em inglês.
- media_type: use "movie" ou "series" conforme o campo Type.
- release_date: converta para formato YYYY-MM-DD.
- plot: reescreva o resumo de forma clara e fluida em português, respeitando o limite do schema.
- genres: transforme o campo Genre em array de strings.
- tags: crie tags relevantes com base no conteúdo, sem exagero.
- actors: transforme o campo Actors em array de strings.
- directors: transforme o campo Director em array de strings, ignorando "N/A".
- writers: transforme o campo Writer em array de strings.
- poster_url: use o campo Poster.
- awards: use o campo Awards, exceto quando for "N/A".
- rating: use imdbRating como number.
- runtime: extraia apenas o valor numérico de Runtime em minutos.
- total_seasons: use totalSeasons apenas quando Type for "series".

Restrições:
- Não adicione campos fora do schema.
- Não retorne strings em campos numéricos.
- Não retorne textos como "N/A"; use null quando apropriado.
- Retorne apenas o JSON final.
"""

EPISODE_SYSTEM_PROMPT = """
Você é um assistente de catalogação de episódios de séries.

Sua tarefa é analisar um objeto JSON de entrada e retornar um novo objeto JSON que siga estritamente o schema de episode.

Regras obrigatórias:
- Retorne somente JSON válido.
- Não inclua explicações, comentários, markdown ou texto adicional.
- Siga exatamente os nomes dos campos definidos no schema.
- Não invente informações.
- Se um campo não estiver disponível ou for "N/A", use null quando o schema permitir.
- Converta valores para os tipos exigidos pelo schema.
- Datas devem estar no formato YYYY-MM-DD.
- Números devem ser retornados como number, não como string.
- Se o título original estiver em inglês, traduza o título principal para português e preserve o original em original_title.
"""

EPISODE_USER_PROMPT = """
Analise o JSON de entrada e produza um JSON de saída compatível com o schema "episode".

Regras de mapeamento:
- title: traduza o título do episódio para português.
- original_title: mantenha o título original em inglês.
- plot: reescreva o resumo de forma clara e fluida em português, respeitando o limite do schema.
- released: converta para formato YYYY-MM-DD.
- season: converta para número inteiro.
- episode: converta para número inteiro.
- rating: use imdbRating como number.

Restrições:
- Não adicione campos fora do schema.
- Não retorne strings em campos numéricos.
- Não retorne textos como "N/A"; use null quando apropriado.
- Retorne apenas o JSON final.
"""


class OpenAIAnalyzer(BaseHttpRequest):
    _BASE_PROMPTS = {
        "media": (MEDIA_SYSTEM_PROMPT, MEDIA_USER_PROMPT),
        "episode": (EPISODE_SYSTEM_PROMPT, EPISODE_USER_PROMPT),
    }

    def __init__(self):
        settings = get_settings()
        headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
        super().__init__(base_url=settings.openai_api_url, headers=headers)
        self.model = settings.openai_model
        self.schemas: Dict[str, Any] = get_json_schemas()

    def _get_payload(self, data: dict) -> dict:
        media_type = "media" if data.get("Type", "media") != "episode" else "episode"
        logger.info(f"Schema data: {type(self.schemas)} {media_type}")
        system_prompt, user_prompt = self._BASE_PROMPTS.get(media_type)
        schema = self.schemas.get(media_type)
        logger.info(f"Schema type: {type(schema)}")
        logger.info(f"Schema data: {schema}")
        user_prompt = f"{user_prompt}\n\nDados de entrada:\n{json.dumps(data, ensure_ascii=False)}"
        user_content = [
            {"type": "input_text", "text": user_prompt}
        ]
        return {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": user_content,
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "summary_output",
                    "strict": True,
                    "schema": schema,
                }
            },
        }

    @staticmethod
    def _normalize_response(response_json: dict) -> dict:
        output = response_json.get("output", [])
        for item in output:
            if item.get("type") != "message":
                continue

            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text")
                    if text:
                        return json.loads(text)

        raise ValueError("Nao foi possível extrair JSON da resposta OpenAI")

    async def analyze_data(self, data: dict) -> dict:
        data = self._get_payload(data)
        r = await self._perform_request("POST", "/responses", json=data)
        return self._normalize_response(r)
