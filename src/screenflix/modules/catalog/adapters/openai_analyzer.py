import json
import re
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
- year: extraia o ano de lançamento como inteiro (YYYY) a partir do campo Year.
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
        super().__init__(base_url=settings.openai_api_url, headers=headers, timeout=360)
        self.model = settings.openai_model
        self.schemas: Dict[str, Any] = get_json_schemas()

    def _resolve_payload_type(self, data: dict, payload_type: str | None = None) -> str:
        if payload_type in self._BASE_PROMPTS:
            return payload_type

        data_type = data.get("Type") or data.get("type")
        if isinstance(data_type, str) and data_type.lower() == "episode":
            return "episode"

        if "Season" in data or "Episode" in data:
            return "episode"

        return "media"

    def _get_payload(self, data: dict, payload_type: str | None = None) -> dict:
        resolved_payload_type = self._resolve_payload_type(data, payload_type=payload_type)
        system_prompt, user_prompt = self._BASE_PROMPTS[resolved_payload_type]
        schema = self.schemas[resolved_payload_type]
        user_prompt = f"{user_prompt}\n\nDados de entrada:\n{json.dumps(data, ensure_ascii=False)}"
        user_content = [
            {"type": "input_text", "text": user_prompt}
        ]
        return {
            "model": self.model,
            "max_output_tokens": 4000,
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
    def _extract_text_output(response_json: dict) -> str:
        text_chunks: list[str] = []
        output = response_json.get("output", [])

        for item in output:
            if item.get("type") != "message":
                continue

            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text")
                    if text:
                        text_chunks.append(text)

        if text_chunks:
            return "".join(text_chunks)

        output_text = response_json.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text

        raise ValueError("Nao foi possível extrair texto da resposta OpenAI")

    @staticmethod
    def _parse_json_output(text: str) -> dict:
        candidate_texts = [text.strip()]

        if candidate_texts[0].startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", candidate_texts[0], flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            candidate_texts.append(cleaned.strip())

        start = candidate_texts[-1].find("{")
        end = candidate_texts[-1].rfind("}")
        if start != -1 and end != -1 and start < end:
            candidate_texts.append(candidate_texts[-1][start:end + 1].strip())

        parse_error: json.JSONDecodeError | None = None
        for candidate in candidate_texts:
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
                if not isinstance(parsed, dict):
                    raise ValueError("Resposta OpenAI não retornou um objeto JSON")
                return parsed
            except json.JSONDecodeError as err:
                parse_error = err

        if parse_error:
            raise ValueError(
                "Nao foi possível interpretar JSON da resposta OpenAI "
                f"(line={parse_error.lineno}, col={parse_error.colno}, msg={parse_error.msg})"
            ) from parse_error

        raise ValueError("Nao foi possível interpretar JSON da resposta OpenAI")

    @classmethod
    def _normalize_response(cls, response_json: dict) -> dict:
        text = cls._extract_text_output(response_json)
        return cls._parse_json_output(text)

    async def analyze_data(self, data: dict, payload_type: str | None = None) -> dict:
        payload = self._get_payload(data, payload_type=payload_type)
        max_attempts = 3
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            response = await self._perform_request("POST", "/responses", json=payload)
            try:
                return self._normalize_response(response)
            except ValueError as err:
                last_error = err
                logger.warning(
                    "OpenAI response normalization failed",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    response_status=response.get("status"),
                    response_id=response.get("id"),
                    error=str(err),
                )

        raise ValueError("Nao foi possível normalizar resposta OpenAI após múltiplas tentativas") from last_error
