from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from screenflix.modules.catalog.adapters.openai_analyzer import OpenAIAnalyzer


@pytest.fixture
def analyzer(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.openai_analyzer.get_settings",
        lambda: SimpleNamespace(openai_api_url="http://openai.local", openai_api_key="key", openai_model="gpt-test"),
    )
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.openai_analyzer.get_json_schemas",
        lambda: {"media": {"type": "object"}, "episode": {"type": "object"}},
    )
    return OpenAIAnalyzer()


def test_resolve_payload_type(analyzer):
    assert analyzer._resolve_payload_type({}, payload_type="media") == "media"
    assert analyzer._resolve_payload_type({"Type": "episode"}) == "episode"
    assert analyzer._resolve_payload_type({"Season": 1}) == "episode"
    assert analyzer._resolve_payload_type({"Type": "movie"}) == "media"


def test_get_payload_structure(analyzer):
    payload = analyzer._get_payload({"Title": "Matrix"}, payload_type="media")

    assert payload["model"] == "gpt-test"
    assert payload["text"]["format"]["schema"] == {"type": "object"}
    assert payload["input"][0]["role"] == "system"
    assert payload["input"][1]["role"] == "user"
    assert "Dados de entrada" in payload["input"][1]["content"][0]["text"]


def test_extract_text_output_from_message(analyzer):
    response = {
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": '{"ok":true}'}],
            }
        ]
    }

    assert analyzer._extract_text_output(response) == '{"ok":true}'


def test_extract_text_output_from_output_text_fallback(analyzer):
    response = {"output": [], "output_text": '{"ok": true}'}
    assert analyzer._extract_text_output(response) == '{"ok": true}'


def test_extract_text_output_raises_when_missing(analyzer):
    with pytest.raises(ValueError, match="extrair texto"):
        analyzer._extract_text_output({"output": []})


@pytest.mark.parametrize(
    "text,expected",
    [
        ('{"a": 1}', {"a": 1}),
        ('```json\n{"a": 2}\n```', {"a": 2}),
        ("noise {\"a\": 3} tail", {"a": 3}),
    ],
)
def test_parse_json_output_happy_paths(analyzer, text, expected):
    assert analyzer._parse_json_output(text) == expected


def test_parse_json_output_raises_for_non_object(analyzer):
    with pytest.raises(ValueError, match="objeto JSON"):
        analyzer._parse_json_output("[1,2,3]")


def test_parse_json_output_raises_for_invalid_json(analyzer):
    with pytest.raises(ValueError, match="interpretar JSON"):
        analyzer._parse_json_output("not json")


def test_normalize_response(analyzer):
    response = {
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": '{"x": 1}'}],
            }
        ]
    }
    assert analyzer._normalize_response(response) == {"x": 1}


@pytest.mark.asyncio
async def test_analyze_data_success_first_attempt(analyzer, monkeypatch):
    monkeypatch.setattr(
        analyzer,
        "_perform_request",
        AsyncMock(
            return_value={
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": '{"ok": true}'}],
                    }
                ]
            }
        ),
    )

    result = await analyzer.analyze_data({"Title": "x"})

    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_analyze_data_retries_and_succeeds(analyzer, monkeypatch):
    responses = [
        {"output": [{"type": "message", "content": [{"type": "output_text", "text": "not-json"}]}]},
        {"output": [{"type": "message", "content": [{"type": "output_text", "text": '{"ok": 1}'}]}]},
    ]

    perform = AsyncMock(side_effect=responses)
    warning = Mock()

    monkeypatch.setattr(analyzer, "_perform_request", perform)
    monkeypatch.setattr("screenflix.modules.catalog.adapters.openai_analyzer.logger.warning", warning)

    result = await analyzer.analyze_data({"Title": "x"})

    assert result == {"ok": 1}
    assert perform.await_count == 2
    warning.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_data_raises_after_max_attempts(analyzer, monkeypatch):
    perform = AsyncMock(
        return_value={
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "bad"}]}]
        }
    )
    monkeypatch.setattr(analyzer, "_perform_request", perform)

    with pytest.raises(ValueError, match="múltiplas tentativas"):
        await analyzer.analyze_data({"Title": "x"})

    assert perform.await_count == 3
