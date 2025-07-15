# tools/gemini_cli.py
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
GEMINI_CLI = os.getenv("GEMINI_CLI")

def ask_gemini_with_file(prompt_text: str, image_path: str = None) -> str:
    if not GEMINI_CLI:
        raise Exception("GEMINI_CLI path not found in .env")
    command = ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, "--yolo"]
    if image_path:
        prompt_text += f"\n[FILE:{image_path}]"
    result = subprocess.run(
        command,
        input=prompt_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    return result.stdout.strip()
