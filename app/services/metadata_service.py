import json
import re
from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.models import FoodMetadata

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_metadata(transcript: str) -> FoodMetadata:

    prompt = f"""
Extract food details from the transcript.

IMPORTANT:
- Return values strictly in English.
- If no food items are found, return an empty list.
- Return JSON only in this format:

{{
  "items": [
    {{
      "foodName": "string",
      "quantity": "string or null",
      "quality": "string or null"
    }}
  ]
}}

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Return strictly valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    # Extract JSON safely
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_match:
        raise ValueError("Invalid JSON from LLM")

    data = json.loads(json_match.group())

    # Ensure items exists
    if not data.get("items"):
        data["items"] = []

    # Normalize each item
    for item in data["items"]:
        if isinstance(item.get("quantity"), (int, float)):
            item["quantity"] = str(item["quantity"])

        item.setdefault("foodName", None)
        item.setdefault("quantity", None)
        item.setdefault("quality", None)

    return FoodMetadata(**data)
