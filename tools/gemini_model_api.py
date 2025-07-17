# tools/gemini_model_api.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# === API Setup ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in environment variables")

genai.configure(api_key=GEMINI_API_KEY)


# === Core Wrapper ===

def ask_gemini_with_file(prompt, image_path, model_name="models/gemini-1.5-flash-latest"):
    """
    Sends a prompt and image file to the specified Gemini model.
    """
    try:
        model = genai.GenerativeModel(model_name)
        with open(image_path, "rb") as f:
            image_data = f.read()

        response = model.generate_content([
            prompt,
            genai.types.ContentPart(
                inline_data=genai.types.Blob(
                    mime_type="image/png",
                    data=image_data
                )
            )
        ])
        return response.text

    except Exception as e:
        print(f"[Gemini] ❌ Model call failed ({model_name}): {e}")
        raise


# === Smart Fallback Utility ===

def smart_vision_query(prompt, image_path):
    """
    Tries Gemini 1.5 Flash first. If it fails, falls back to 1.5 Pro.
    """
    try:
        print("[Gemini API] ⚡ Trying Gemini Flash...")
        return ask_gemini_with_file(prompt, image_path, model_name="models/gemini-1.5-flash-latest")
    except Exception as flash_error:
        print(f"[Gemini API] ⚠️ Flash failed, trying Pro...\n{flash_error}")
        try:
            print("[Gemini API] 🧠 Trying Gemini Pro...")
            return ask_gemini_with_file(prompt, image_path, model_name="models/gemini-1.5-pro-latest")
        except Exception as pro_error:
            print(f"[Gemini API] ❌ Pro model also failed:\n{pro_error}")
            return "[]"
