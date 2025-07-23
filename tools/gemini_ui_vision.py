# tools/gemini_ui_vision.py

import os
import json
import re
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import numpy as np
import logging
from dotenv import load_dotenv

# Load environment variables at the top of the module
load_dotenv()

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure the API key once
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY environment variable not set. API calls will fail.")

# Define model constants for easy management
DEFAULT_MODELS = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"]


def encode_image_to_webp_bytes(pixels: np.ndarray) -> bytes | None:
    """
    Compresses a NumPy RGB image array to in-memory WebP bytes.
    """
    try:
        img = Image.fromarray(pixels.astype("uint8"), "RGB")
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=95)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Failed to encode image to WebP bytes: {e}", exc_info=True)
        return None


def smart_vision_query(pixels: np.ndarray, prompt: str, models=DEFAULT_MODELS) -> str | None:
    """
    Performs a vision query using in-memory image data, with a model fallback system.
    """
    if not GEMINI_API_KEY:
        logger.error("Cannot make API call without API key.")
        return None

    image_bytes = encode_image_to_webp_bytes(pixels)
    if not image_bytes:
        return None # Error is already logged

    image_part = {
        "mime_type": "image/webp",
        "data": image_bytes
    }

    for model_name in models:
        try:
            logger.info(f"Querying model `{model_name}`...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                [prompt, image_part],
                generation_config={"temperature": 0.1}, # Low temp for deterministic UI analysis
                stream=False
            )
            if response and response.text:
                logger.info(f"Model `{model_name}` succeeded.")
                return response.text
        except Exception as e:
            logger.warning(f"Model `{model_name}` failed: {e}")
            continue # Try the next model

    logger.error("All models failed to generate a response.")
    return None


def _parse_json_from_response(response_text: str) -> dict | list | None:
    """
    A robust utility to find and parse a JSON object or list from a model's raw text output.
    """
    # --- FIX: Use a more flexible regex that finds either a JSON object or an array ---
    match = re.search(r'(\{.*\}|\[.*\])', response_text, re.DOTALL)
    
    if not match:
        logger.error("No valid JSON object or array found in the response.")
        logger.debug(f"Raw response for debugging:\n{response_text}")
        return None
    
    json_string = match.group(0)
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse cleaned JSON: {e}")
        logger.debug(f"String passed to parser:\n{json_string}")
        return None


def analyze_ui_elements_from_pixels(pixels: np.ndarray, task_prompt: str) -> list:
    """
    A high-level function specifically for getting a LIST of UI elements.
    """
    system_prompt = (
        "You are an expert UI analyst. Your task is to detect all UI elements relevant to the user's goal "
        "from the provided screen capture. For each element, you must return:\n"
        "- `label`: A short, descriptive name (e.g., 'Post', 'Login button').\n"
        "- `bounding_box`: A dictionary with `x_min`, `y_min`, `x_max`, `y_max` keys. These must be absolute screen coordinates.\n"
        "- `confidence`: Your confidence in the detection from 0.0 to 1.0.\n"
        "- `context`: A brief description of the element's location or purpose (e.g., 'main composer popup', 'left sidebar').\n\n"
        "Respond in a valid JSON list format ONLY. Do not include markdown fences or any other text."
    )

    full_prompt = f"{system_prompt}\n\nUSER TASK:\n`{task_prompt}`"
    
    response_text = smart_vision_query(pixels, full_prompt)

    if not response_text:
        return []

    parsed_json = _parse_json_from_response(response_text)
    # Ensure the result is a list, as expected by the caller
    return parsed_json if isinstance(parsed_json, list) else []

