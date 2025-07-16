# tools/gemini_interface.py

import json
import numpy as np
import tempfile
from PIL import Image, ImageDraw
from .gemini_cli import ask_gemini_with_file


def strip_code_wrappers(text):
    """
    Strips markdown code block wrappers from Gemini responses.
    """
    if text.strip().startswith("```"):
        lines = text.strip().splitlines()
        return "\n".join(line for line in lines if not line.strip().startswith("```"))
    return text.strip()


def ask_gemini(prompt_text):
    """
    Text-only Gemini query interface.
    """
    return ask_gemini_with_file(prompt_text)


def find_buttons_with_metadata(pixel_array, target_label="Post", multi=True):
    """
    Uses Gemini to locate UI buttons by label.
    Returns bounding box, confidence, and context.
    """
    try:
        img = Image.fromarray(pixel_array.astype("uint8"), "RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            img.save(tmp.name, format="PNG")
            image_path = tmp.name
    except Exception as e:
        raise Exception(f"[Gemini Interface] ❌ Failed to convert pixel array to image: {e}")

    prompt = f"""
You are a visual UI assistant.

TASK:
Find all buttons labeled "{target_label}" in the attached screenshot.

Respond with valid JSON list of objects:
[
  {{
    "label": "Post",
    "x_min": 500,
    "y_min": 200,
    "x_max": 570,
    "y_max": 240,
    "confidence": 0.93,
    "context": "popup composer"
  }},
  ...
]

✅ Use bounding box keys: x_min, y_min, x_max, y_max.
✅ Only include buttons that match the label and are likely intended for the user.
✅ Add a 'confidence' score and a brief 'context' string.

Respond with **valid JSON only**. No extra words.
"""

    print(f"[Gemini Interface] 🧠 Analyzing UI for: '{target_label}' (multi={multi})")
    response = ask_gemini_with_file(prompt, image_path)

    try:
        cleaned = strip_code_wrappers(response)
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            parsed = [parsed]

        return parsed
    except Exception as e:
        print(f"[Gemini Interface] ❌ Failed to parse Gemini response:\n{response}")
        return []


def save_debug_visualization(pixel_array, buttons, filename="debug_output.png"):
    """
    Saves an annotated debug image with bounding boxes and metadata.
    """
    try:
        img = Image.fromarray(np.array(pixel_array).astype("uint8"), "RGB").copy()
        draw = ImageDraw.Draw(img)

        for button in buttons:
            label = button.get("label", "Button")
            confidence = button.get("confidence", 0)

            if all(k in button for k in ["x_min", "y_min", "x_max", "y_max"]):
                box = (button["x_min"], button["y_min"], button["x_max"], button["y_max"])
                draw.rectangle(box, outline="red", width=2)
                draw.text((box[0] + 3, box[1] - 12), f"{label} ({confidence:.2f})", fill="yellow")
            elif "x" in button and "y" in button:
                x, y = button["x"], button["y"]
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="red", outline="black")
                draw.text((x + 8, y - 10), f"{label} ({confidence:.2f})", fill="yellow")

        img.save(filename)
        print(f"[Gemini Interface] 📸 Debug image saved to '{filename}'")
    except Exception as e:
        print(f"[Gemini Interface] ❌ Failed to save debug visualization: {e}")
