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
    """
    Convert any unit to KG.
    grams → kg
    ml → kg
    liter → kg
    """
    if not quantity:
        return None

    q = quantity.lower()
    #"2 KG" → "2 kg"

    try:
        value = float(q.split()[0]) #Extracts the number from quantity. ["2","kg"]
    except Exception:
        return None

    
    if "g" in q or "gram" in q:
        value = value / 1000

    
    elif "ml" in q:
        value = value / 1000

    
    elif "liter" in q or "litre" in q:
        pass

    
    elif "kg" in q or "kilo" in q:
        pass

    return f"{round(value,3)} kg" #0.5234234 -> 0.523 kg


def build_prompt(transcript: str) -> str:
    return f"""
You are an information extraction system.

TASK:
Extract food purchase details from the transcript.

IMPORTANT RULES:
- The transcript may be in ANY language.
- Translate all food names to English.
- Return ONLY valid JSON.
- All output text MUST be in English.

QUANTITY RULES:
- ALL quantities must be returned ONLY in "kg".
- Convert grams → kg.
- Convert ml → kg.
- Convert liter → kg.
- If conversion is unclear assume 1 liter = 1 kg.

If no food items exist return an empty list.

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
                {
                    "role": "system",
                    "content": "You extract structured food metadata from multilingual text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        if not data.get("items"):
            data["items"] = []

        cleaned_items = []

        for item in data["items"]:

            quantity = normalize_unit(item.get("quantity"))

            cleaned_items.append({
                "foodName": item.get("foodName"),
                "quantity": quantity,
                "quality": item.get("quality")
            })

        data["items"] = cleaned_items

        return FoodMetadata(**data)

    except json.JSONDecodeError as e:
        raise MetadataExtractionError("Invalid JSON returned by LLM") from e

    except ValidationError as e:
        raise MetadataExtractionError("Metadata schema validation failed") from e

    except Exception as e:
        raise MetadataExtractionError("Metadata extraction failed") from e