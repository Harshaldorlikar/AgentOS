# tools/gemini_ui_vision.py

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


def analyze_ui_elements_from_pixels(pixel_array, task_prompt, context_note=None):
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
This is a screenshot of the agent’s current view while attempting the task:
→ "{task_prompt}"

The agent needs help **perceiving** the screen visually in order to complete its mission.
You are acting as the agent's eyes — your job is to help them locate the correct UI elements and guide them in completing the task.

{f"NOTE: {context_note}" if context_note else ""}

Return a structured JSON list of all helpful UI elements relevant to the task:
[
  {{
    "label": "Post",
    "x_min": ..., "y_min": ..., "x_max": ..., "y_max": ...,
    "confidence": ...,  # 0.0 to 1.0
    "context": "brief description of region (e.g. 'popup composer', 'sidebar')"
  }}
]

✅ Focus only on elements relevant to the goal.
✅ Use label 'Post' only if the button will actually submit the tweet.
✅ Include context for each element to help the agent choose the right one.
✅ Use coordinates and bounding box dimensions for safe clicking.

Respond with **valid JSON only**. No extra words.
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
