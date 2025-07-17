# tools/gemini_ui_vision.py

import os
import base64
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import numpy as np

# Load your one API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "your_api_key_here"
genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_MODELS = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"]


def encode_image_to_webp_base64(pixels: np.ndarray) -> str:
    """
    Compresses and encodes a NumPy RGB image array to base64 WebP format.
    """
    img = Image.fromarray(pixels.astype("uint8"), "RGB")
    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=80)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def smart_vision_query(pixels: np.ndarray, prompt: str, models=DEFAULT_MODELS):
    """
    Attempts vision queries with Flash first, falls back to Pro if needed.
    Returns structured response or None.
    """
    img_data = encode_image_to_webp_base64(pixels)
    image_part = {
        "mime_type": "image/webp",
        "data": base64.b64decode(img_data)
    }

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                [prompt, image_part],
                stream=False
            )
            if response and response.text:
                print(f"[GeminiVision] ✅ Model `{model_name}` succeeded.")
                return response.text
        except Exception as e:
            print(f"[GeminiVision] ⚠️ Model `{model_name}` failed: {e}")
            continue

    print("[GeminiVision] ❌ All models failed.")
    return None


def analyze_ui_elements_from_pixels(pixels: np.ndarray, prompt: str) -> list:
    """
    Uses smart_vision_query to send screen and extract UI elements.
    Returns list of elements with bounding boxes, confidence, labels.
    """
    system_prompt = (
        "You are an expert UI analyst. Given an image of a screen and a task, "
        "detect all relevant UI elements. For each element, return:\n"
        "- label (e.g., 'Post', 'Like')\n"
        "- bounding box: x_min, y_min, x_max, y_max (absolute screen coords)\n"
        "- confidence (0.0 to 1.0)\n"
        "- context (e.g., 'popup', 'sidebar')\n\n"
        "Respond in JSON list format ONLY."
    )

    full_prompt = f"{system_prompt}\n\nTASK:\n{prompt}"
    response = smart_vision_query(pixels, full_prompt)

    if not response:
        return []

    try:
        import json
        return json.loads(response)
    except Exception as e:
        print(f"[GeminiVision] ❌ Failed to parse response: {e}")
        return []
