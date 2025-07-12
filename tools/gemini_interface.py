# tools/gemini_interface.py

import base64
import json
import numpy as np
import tempfile

def ask_gemini(prompt_text):
	"""
	Sends a text-only prompt to Gemini via the CLI and returns its response.
	"""
	from tools.runtime_controller import RuntimeController
	return RuntimeController.ask_gemini_with_file(prompt_text)

def find_button_from_pixels(pixel_array, target_label="Post"):
	"""
	Sends raw pixel data to Gemini to locate the specified button.
	Expects pixel_array as a NumPy array (e.g. from PIL.ImageGrab().convert('RGB')).
	Returns: dict like { "x": 123, "y": 456, "label": "Post" }
	"""
	try:
		from PIL import Image
		img = Image.fromarray(pixel_array.astype('uint8'), 'RGB')
		with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
			img.save(tmp.name, format="PNG")
			image_path = tmp.name
	except Exception as e:
		raise Exception(f"[Gemini Interface] Failed to convert pixel array to image: {e}")

	prompt = f"""
You are a visual UI agent. You will be given a screenshot of a computer screen.
Your job is to identify the screen coordinates of a button labeled '{target_label}'.
Please return only a JSON object like:
{{ "x": 1234, "y": 567, "label": "{target_label}" }}
The coordinates should point to the center of the clickable area.
Only respond with the JSON. No extra words.
"""
	print(f"[Gemini Interface] 🧠 Sending image to Gemini to locate: '{target_label}'")

	from tools.runtime_controller import RuntimeController
	response = RuntimeController.ask_gemini_with_file(prompt_text=prompt + f"\n[FILE:{image_path}]")

	try:
		return json.loads(response)
	except Exception as e:
		print(f"[Gemini Interface] ❌ Failed to parse Gemini response:\n{response}")
		return None