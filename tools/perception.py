# tools/perception.py

import time
import numpy as np
from PIL import ImageGrab
import hashlib
import os

PERCEPTION_FILE = "memory/perception_snap.npy"
HASH_RECORD = "memory/last_hash.txt"
PNG_DEBUG = "memory/perception_debug.png"

def grab_screen_array():
    img = ImageGrab.grab()
    return np.array(img.convert("RGB"))

def hash_array(arr: np.ndarray):
    return hashlib.sha1(arr.tobytes()).hexdigest()

def load_last_hash():
    try:
        with open(HASH_RECORD, "r") as f:
            return f.read().strip()
    except:
        return ""

def save_last_hash(h):
    with open(HASH_RECORD, "w") as f:
        f.write(h)

def save_array(arr: np.ndarray, path=PERCEPTION_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.save(path, arr)

def save_debug_png(arr: np.ndarray):
    from PIL import Image
    img = Image.fromarray(arr)
    img.save(PNG_DEBUG)

def check_and_update_perception():
    arr = grab_screen_array()
    new_hash = hash_array(arr)
    old_hash = load_last_hash()

    if new_hash != old_hash:
        print("[Perception] ⚡ Visual change detected.")
        save_array(arr)
        save_debug_png(arr)
        save_last_hash(new_hash)
        return arr
    else:
        print("[Perception] 💤 No visual change.")
        return None