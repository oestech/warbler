import pytest

from app.llm import extract_filter, parse_query


# Shape recorded from a real Interactions API response (2026-08-27).
RECORDED_INTERACTION = {
    "id": "v1_abc123",
    "status": "completed",
    "object": "interaction",
    "model": "gemini-3.5-flash-lite",
    "steps": [
        {"signature": "abc", "type": "thought"},
        {
            "type": "model_output",
            "content": [
                {
                    "type": "text",
                    "text": (
                        '{"op": "and", "clauses": [{"field": "tag", "cmp": "eq",'
                        ' "value": "volunteer"}, {"field": "city", "cmp": "eq",'
                        ' "value": "Houston"}]}'
                    ),
                }
            ],
        },
    ],
}


def test_extract_filter_steps_shape():
    assert extract_filter(RECORDED_INTERACTION) == {
        "op": "and",
        "clauses": [
            {"field": "tag", "cmp": "eq", "value": "volunteer"},
            {"field": "city", "cmp": "eq", "value": "Houston"},
        ],
    }


def test_extract_filter_output_text_shape():
    assert extract_filter({"output_text": '{"op": "and", "clauses": []}'}) == {
        "op": "and",
        "clauses": [],
    }


def test_extract_filter_unexpected_shape():
    with pytest.raises(RuntimeError):
        extract_filter({"something_else": True})


def test_parse_query_requires_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        parse_query("volunteers in houston")
