import json, tempfile
import numpy as np
from PIL import Image
from tools.gemini_cli import ask_gemini_with_file
from tools.debug_visualizer import draw_button_overlay


def strip_code_wrappers(text):
    """
    Strips triple-backtick markdown code fences (e.g., ```json ... ```) from Gemini responses.
    """
    if text.strip().startswith("```"):
        lines = text.strip().splitlines()
        return "\n".join(line for line in lines if not line.strip().startswith("```"))
    return text.strip()


def analyze_ui_elements_from_pixels(pixel_array, task_prompt):
    """
    Vision assistant using Gemini + screenshot to extract UI elements.

    Returns list of:
    {
      "label": "Post",
      "x_min": 500,
      "y_min": 400,
      "x_max": 550,
      "y_max": 430,
      "confidence": 0.92,
      "context": "popup composer"
    }
    """
    try:
        img = Image.fromarray(pixel_array.astype("uint8"), "RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            img.save(tmp.name, format="PNG")
            image_path = tmp.name
    except Exception as e:
        raise Exception(f"[Gemini Vision] Image conversion failed: {e}")

    prompt = f"""
You are a vision assistant helping agents interact with complex user interfaces.

TASK:
{task_prompt}

Analyze the screenshot and respond ONLY with this format:

[
  {{
    "label": "Post",
    "x_min": 520,
    "y_min": 420,
    "x_max": 570,
    "y_max": 440,
    "confidence": 0.92,
    "context": "popup composer"
  }},
  ...
]

✅ Only include UI elements that help complete the task.
✅ Use 'label': "Post" only for the correct clickable button.
✅ Add bounding box coordinates — not just a center point.
✅ Provide a confidence score (0.0 to 1.0) and a short context description.

⚠️ Respond with **valid JSON only**. No markdown. No commentary.
    """

    print("[Gemini Vision] 🧠 Analyzing UI for task...")
    response = ask_gemini_with_file(prompt, image_path)

    try:
        cleaned = strip_code_wrappers(response)
        parsed = json.loads(cleaned)

        if not isinstance(parsed, list):
            print(f"[Gemini Vision] ⚠️ Response was not a list. Got:\n{parsed}")
            return []

        # Optional: render debug overlay
        try:
            draw_button_overlay(pixel_array, parsed, image_path)
        except Exception as viz_err:
            print(f"[Gemini Vision] ⚠️ Debug overlay failed: {viz_err}")

        return parsed

    except Exception as e:
        print(f"[Gemini Vision] ❌ Failed to parse Gemini response:\n{response}")
        return []
