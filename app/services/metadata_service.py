import json
import asyncio
from openai import OpenAI
from pydantic import ValidationError
from app.models import FoodMetadata
from app.core.config import settings


class MetadataExtractionError(Exception):
    """Custom exception raised when metadata extraction fails"""
    pass


def normalize_unit(quantity: str | None):
    """
    Normalize quantity values to kilograms (kg).

    Supported conversions:
    - grams → kg
    - ml → kg
    - liter → kg

    If unit is already kg it remains unchanged.
    Returns a string formatted as '<value> kg'.
    """
    if not quantity:
        return None

    q = quantity.lower()

    # Extract numeric value from quantity string
    try:
        value = float(q.split()[0])
    except Exception:
        # Return None if quantity cannot be parsed
        return None

    # Check KG first to avoid misinterpreting "kg" as "g"
    if "kg" in q or "kilo" in q:
        pass

    # Convert grams to kg
    elif "gram" in q or " g" in q:
        value = value / 1000

    # Convert milliliters to kg (assume density ≈ water)
    elif "ml" in q:
        value = value / 1000

    # Liter assumed equivalent to kg
    elif "liter" in q or "litre" in q:
        pass

    return f"{round(value,3)} kg"


def build_prompt(transcript: str) -> str:
    """
    Build the LLM prompt used to extract structured food metadata
    from a multilingual transcript.
    """
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


def _call_openai(prompt: str):
    """
    Calls OpenAI API to extract structured metadata.

    A new client instance is created per call to ensure thread safety
    when used with asyncio thread pools.
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    return client.chat.completions.create(
        model=settings.METADATA_EXTRACTION_MODEL,
        response_format={"type": "json_object"},  # Force valid JSON response
        temperature=settings.MODEL_TEMPERATURE,
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


async def extract_metadata(transcript: str) -> FoodMetadata:
    """
    Main metadata extraction pipeline.

    Steps:
    1. Build LLM prompt
    2. Call OpenAI API asynchronously
    3. Parse JSON response
    4. Normalize quantities to kg
    5. Validate against FoodMetadata schema
    """
    try:
        prompt = build_prompt(transcript)

        # Run blocking OpenAI API call in thread pool
        response = await asyncio.to_thread(_call_openai, prompt)

        # Extract JSON content from response
        content = response.choices[0].message.content
        data = json.loads(content)

        # Ensure items key exists
        if not data.get("items"):
            data["items"] = []

        cleaned_items = []

        # Normalize quantities and sanitize items
        for item in data["items"]:
            quantity = normalize_unit(item.get("quantity"))

            cleaned_items.append({
                "foodName": item.get("foodName"),
                "quantity": quantity,
                "quality": item.get("quality")
            })

        data["items"] = cleaned_items

        # Validate output using Pydantic model
        return FoodMetadata(**data)

    except json.JSONDecodeError as e:
        raise MetadataExtractionError("Invalid JSON returned by LLM") from e

    except ValidationError as e:
        raise MetadataExtractionError("Metadata schema validation failed") from e

    except Exception as e:
        raise MetadataExtractionError("Metadata extraction failed") from e