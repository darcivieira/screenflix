import json
import re
from typing import Dict, Any

from screenflix.core.logging.logger import get_logger
from screenflix.core.settings import get_settings
from screenflix.core.utils.shortcuts import get_json_schemas
from screenflix.modules.catalog.adapters.base_http_request import BaseHttpRequest

logger = get_logger(__name__)

MEDIA_SYSTEM_PROMPT = """
Você é um especialista em catalogação de filmes e séries para um catálogo pessoal.

Sua função é transformar um JSON bruto de entrada em um JSON final rigorosamente compatível com o schema fornecido pela aplicação.

Objetivo principal:
- Organizar, limpar, normalizar e enriquecer moderadamente os dados de filmes e séries.
- Produzir um resultado confiável, consistente e adequado para armazenamento em catálogo.
- Priorizar precisão factual, legibilidade em português e padronização dos campos.

Regras obrigatórias:
- Retorne somente um objeto JSON válido.
- Não escreva explicações, comentários, markdown, cabeçalhos ou texto fora do JSON.
- Respeite exatamente os nomes dos campos definidos no schema.
- Não adicione campos extras.
- Não invente fatos que não possam ser inferidos com segurança a partir do JSON recebido.
- Sempre normalize valores textuais removendo espaços excedentes, quebras de linha desnecessárias e caracteres decorativos inúteis.
- Nunca retorne valores literais como "N/A", "Unknown", "null", "-", "--" ou string vazia quando representarem ausência de dado.
- Converta os valores para os tipos exigidos pelo schema.
- Datas devem estar no formato YYYY-MM-DD.
- Campos numéricos devem ser numéricos de fato, nunca string.
- Campos de lista devem conter apenas strings limpas, sem duplicidade, sem itens vazios e sem espaços excedentes.
- Preserve nomes próprios, nomes de franquias, personagens, lugares e empresas quando a tradução não fizer sentido.
- Não traduza nomes de pessoas.
- Não use emojis.
- Não use HTML.
- Não use barras invertidas desnecessárias, aspas escapadas sem necessidade ou caracteres especiais inúteis.
- O texto deve soar natural em português do Brasil.

Regras semânticas:
- Identifique corretamente se o conteúdo é filme ou série.
- Para filme, use media_type = "movie".
- Para série, use media_type = "series".
- O campo title deve refletir o título mais adequado para exibição no catálogo em português do Brasil.
- O campo original_title deve preservar o título original da obra.
- O campo plot deve ser uma sinopse em português do Brasil, clara, coesa, informativa e sem spoilers desnecessários.
- O campo plot não deve repetir listas técnicas como elenco, direção, duração, notas ou premiações.
- O campo plot não deve começar com expressões como "Este filme conta", "Esta série conta", "A trama acompanha" repetidas mecanicamente em todas as respostas; varie a redação de forma natural.
- O campo tags deve conter poucas tags relevantes e úteis para navegação no catálogo, evitando excesso, generalidades e redundâncias.
"""

MEDIA_USER_PROMPT = """
Analise o JSON de entrada e produza um JSON de saída compatível com o schema "media".

Mapeamento dos campos:

1. title
- Use o título mais adequado para exibição em português do Brasil.
- Priorize o título oficialmente conhecido no Brasil, quando isso puder ser inferido com segurança a partir do payload.
- Se não houver base suficiente para afirmar um título brasileiro diferente, use o título original como title.
- Remova enfeites, sufixos promocionais, prefixos desnecessários e caracteres inúteis.

2. original_title
- Preserve o título original da obra.
- Não traduza.
- Não inclua ano, edição, mídia, resolução ou observações extras.

3. media_type
- Use "movie" ou "series" conforme o tipo da obra.
- Baseie-se principalmente no campo Type.
- Se houver conflito no payload, use a interpretação mais consistente com os demais campos.

4. year
- Extraia o ano principal de lançamento como inteiro.
- Se o campo Year vier em formatos como "2010–2013", use o primeiro ano.
- Nunca retorne texto.

5. release_date
- Converta a data de lançamento para YYYY-MM-DD.
- Se houver apenas data parcial ou impossível de normalizar com segurança, use o valor mais preciso possível apenas se o schema permitir; caso contrário, infira somente quando o payload trouxer elementos suficientes.
- Não invente dia ou mês sem base.

6. plot
- Reescreva a sinopse em português do Brasil.
- O texto deve ser claro, limpo, fluido e adequado para catálogo.
- Preserve o sentido do enredo original.
- Não invente eventos, personagens, conflitos ou desfechos que não estejam sustentados pelo payload.
- Evite spoilers diretos, especialmente de finais, reviravoltas ou revelações centrais.
- Não repita o título da obra em excesso.
- Não use frases genéricas vazias.
- Não inclua notas técnicas, elenco, prêmios ou duração dentro do plot.
- Se a sinopse original vier muito curta, você pode expandi-la moderadamente apenas para melhorar clareza e coesão, sem criar fatos novos.
- Entregue um texto natural, sem caracteres especiais inúteis e sem marcas promocionais.

7. genres
- Converta o campo Genre em lista de strings.
- Separe por vírgula quando necessário.
- Normalize capitalização e espaços.
- Remova duplicados e itens vazios.

8. tags
- Gere entre 3 e 8 tags realmente úteis para indexação no catálogo.
- As tags devem refletir temas, tom, ambientação, estrutura narrativa, público ou características marcantes da obra.
- Evite repetir exatamente os gêneros já presentes em genres, salvo quando isso for inevitável.
- Evite tags genéricas demais como "filme", "série", "legal", "bom", "drama" se já estiver em genres.
- Exemplos de boas tags: "distopia", "viagem no tempo", "investigação", "suspense psicológico", "família", "sobrevivência", "cyberpunk", "coming of age".

9. actors
- Converta o campo Actors em lista de strings.
- Preserve apenas nomes.
- Remova "N/A", duplicados, itens vazios e espaços excedentes.

10. directors
- Converta o campo Director em lista de strings.
- Preserve apenas nomes.
- Ignore "N/A", duplicados, itens vazios e espaços excedentes.

11. writers
- Converta o campo Writer em lista de strings.
- Preserve apenas nomes.
- Ignore "N/A", duplicados, itens vazios e espaços excedentes.

12. poster_url
- Use o campo Poster.
- Se o valor indicar ausência de imagem, trate conforme o schema.

13. awards
- Use o conteúdo de Awards apenas quando houver informação real.
- Não reescreva de forma promocional.
- Preserve de forma limpa e objetiva.

14. rating
- Use imdbRating convertido para number.
- Se vier inválido, ausente ou não numérico, trate conforme o schema.

15. runtime
- Extraia apenas o número de minutos a partir de Runtime.
- Exemplo: "142 min" -> 142
- Nunca retorne string.

16. total_seasons
- Use totalSeasons apenas quando a obra for série.
- Quando for filme, siga a convenção esperada pelo schema e pela aplicação.
- Nunca retorne string.

Restrições finais:
- Não adicione campos fora do schema.
- Não use placeholders textuais para ausência de dados.
- Não produza conteúdo promocional, opinativo ou sensacionalista.
- O JSON final deve estar pronto para persistência em catálogo audiovisual.
"""

EPISODE_SYSTEM_PROMPT = """
Você é um especialista em catalogação de episódios de séries para um catálogo pessoal.

Sua função é transformar um JSON bruto de entrada em um JSON final rigorosamente compatível com o schema de episode fornecido pela aplicação.

Objetivo principal:
- Organizar, limpar, normalizar e enriquecer moderadamente os dados de episódios.
- Produzir um resultado confiável, consistente e adequado para armazenamento em catálogo.
- Priorizar precisão factual, legibilidade em português e padronização dos campos.

Regras obrigatórias:
- Retorne somente um objeto JSON válido.
- Não escreva explicações, comentários, markdown, cabeçalhos ou texto fora do JSON.
- Respeite exatamente os nomes dos campos definidos no schema.
- Não adicione campos extras.
- Não invente fatos que não possam ser inferidos com segurança a partir do JSON recebido.
- Sempre normalize valores textuais removendo espaços excedentes, quebras de linha desnecessárias e caracteres decorativos inúteis.
- Nunca retorne valores literais como "N/A", "Unknown", "null", "-", "--" ou string vazia quando representarem ausência de dado.
- Converta os valores para os tipos exigidos pelo schema.
- Datas devem estar no formato YYYY-MM-DD.
- Campos numéricos devem ser numéricos de fato, nunca string.
- Preserve nomes próprios, nomes de personagens, lugares, facções, franquias e organizações quando a tradução não fizer sentido.
- Não traduza nomes de pessoas.
- Não use emojis.
- Não use HTML.
- Não use barras invertidas desnecessárias, aspas escapadas sem necessidade ou caracteres especiais inúteis.
- O texto deve soar natural em português do Brasil.

Regras semânticas:
- O campo title deve refletir o nome do episódio em português do Brasil, quando isso fizer sentido.
- O campo original_title deve preservar o título original do episódio.
- O campo plot deve ser uma sinopse em português do Brasil, clara, coesa, informativa e sem spoilers desnecessários.
- O campo plot deve focar no enredo do episódio, não em opinião, crítica ou metadados técnicos.
"""

EPISODE_USER_PROMPT = """
Analise o JSON de entrada e produza um JSON de saída compatível com o schema "episode".

Mapeamento dos campos:

1. title
- Traduza o título do episódio para português do Brasil quando isso fizer sentido para catálogo.
- Preserve nomes próprios, nomes de lugares, organizações, eventos e expressões consagradas quando a tradução literal empobrecer ou distorcer o sentido.
- Remova caracteres decorativos e ruídos textuais.

2. original_title
- Preserve o título original do episódio.
- Não traduza.
- Não inclua informações extras.

3. plot
- Reescreva a sinopse do episódio em português do Brasil.
- O texto deve ser claro, limpo, fluido e adequado para catálogo.
- Preserve o sentido do enredo original.
- Não invente acontecimentos, relações, revelações ou consequências não sustentadas pelo payload.
- Evite spoilers diretos, especialmente reviravoltas e finais.
- Não descreva avaliação crítica ou opinião.
- Não inclua nota, temporada, número do episódio, data, elenco ou outros metadados dentro do plot.
- Se a sinopse original vier muito curta, você pode expandi-la moderadamente apenas para melhorar clareza e coesão, sem criar fatos novos.
- Entregue um texto natural, sem caracteres especiais inúteis.

4. released
- Converta a data para YYYY-MM-DD.
- Não invente partes ausentes da data.

5. poster_url
- Use a URL da imagem do episódio quando disponível.
- Se estiver ausente ou inválida, trate conforme o schema.

6. season
- Converta Season para número.
- Nunca retorne string.

7. episode
- Converta Episode para número.
- Nunca retorne string.

8. rating
- Use imdbRating convertido para number.
- Se vier inválido, ausente ou não numérico, trate conforme o schema.

Restrições finais:
- Não adicione campos fora do schema.
- Não use placeholders textuais para ausência de dados.
- Não produza conteúdo promocional, opinativo ou sensacionalista.
- O JSON final deve estar pronto para persistência em catálogo audiovisual.
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
