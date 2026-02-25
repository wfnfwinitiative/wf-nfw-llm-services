import json
from openai import OpenAI
from pydantic import ValidationError
from app.config import OPENAI_API_KEY
from app.models import FoodMetadata

client = OpenAI(api_key=OPENAI_API_KEY)


class MetadataExtractionError(Exception):
    """Raised when metadata extraction fails"""
    pass


def normalize_unit(quantity: str | None):
    if not quantity:
        return None

    q = quantity.lower()

    weight_words = ["kg", "kilo", "kilogram", "g", "gram", "grams"]
    liquid_words = ["liter", "litre", "ml", "milliliter", "millilitre"]

    if any(w in q for w in weight_words):
        return quantity.split()[0] + " kg" if quantity.split() else "kg"

    if any(w in q for w in liquid_words):
        return quantity.split()[0] + " liter" if quantity.split() else "liter"

    return quantity


def build_prompt(transcript: str) -> str:
    return f"""
You are an information extraction system.

TASK:
Extract food purchase details from the transcript.

RULES:
- Return ONLY valid JSON.
- All text must be in English.
- Quantity unit must be ONLY "kg" or "liter" when present.
- Convert grams → kg and ml → liter when possible.
- If no food items exist, return an empty list.
- Do not hallucinate items.

OUTPUT FORMAT:
{{
  "items": [
    {{
      "foodName": "string",
      "quantity": "string or null",
      "quality": "string or null"
    }}
  ]
}}

TRANSCRIPT:
{transcript}
"""


def extract_metadata(transcript: str) -> FoodMetadata:
    try:
        prompt = build_prompt(transcript)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},  
            temperature=0,
            messages=[
                {"role": "system", "content": "You extract structured food metadata."},
                {"role": "user", "content": prompt}
            ],
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        # Ensure items key exists
        if not data.get("items"):
            data["items"] = []

        for item in data["items"]:
            if isinstance(item.get("quantity"), (int, float)):
                item["quantity"] = str(item["quantity"])

            item["quantity"] = normalize_unit(item.get("quantity"))

            item.setdefault("foodName", None)
            item.setdefault("quantity", None)
            item.setdefault("quality", None)

        return FoodMetadata(**data)

    except json.JSONDecodeError as e:
        raise MetadataExtractionError("Invalid JSON returned by LLM") from e

    except ValidationError as e:
        raise MetadataExtractionError("Metadata schema validation failed") from e

    except Exception as e:
        raise MetadataExtractionError("Metadata extraction failed") from e