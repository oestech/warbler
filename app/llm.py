"""Turns a people-search phrase into filter JSON using Gemini Flash Lite."""

import json
import os

import httpx

GEMINI_MODEL = "gemini-3.5-flash-lite"
API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

INSTRUCTIONS = """\
Convert the people-search phrase from a CRM into filter JSON.
Schema: {"op": "and", "clauses": [{"field": ..., "cmp": "eq" or "contains", "value": ...}]}
Person fields: city, state, tag, email. Tags are short lowercase labels such as
volunteer, canvasser, donor, host. For state, always output the two-letter code
(TX, OK) even when the user writes the state name. For every other field, copy
the value exactly as the user wrote it. If nothing in the phrase maps to a
filter, return {"op": "and", "clauses": []}. Respond with only the JSON.

Phrase: """

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "op": {"type": "string"},
        "clauses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "cmp": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["field", "cmp", "value"],
            },
        },
    },
    "required": ["op", "clauses"],
}


def parse_query(text: str) -> dict:
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    resp = httpx.post(
        API_URL,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "model": GEMINI_MODEL,
            "input": INSTRUCTIONS + text.strip(),
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": RESPONSE_SCHEMA,
            },
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return extract_filter(resp.json())


def extract_filter(interaction: dict) -> dict:
    text = interaction.get("output_text") or interaction.get("outputText")
    if text is None:
        for step in interaction.get("steps", []):
            if step.get("type") != "model_output":
                continue
            for part in step.get("content", []):
                if part.get("type") == "text" and part.get("text"):
                    text = part["text"]
    if text is None:
        raise RuntimeError(
            f"unexpected interaction shape; top-level keys: {sorted(interaction)}"
        )
    return json.loads(text)
