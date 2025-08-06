# tools/button_overlay_visualizer.py

import numpy as np
import cv2
from typing import List, Dict, Optional
from PIL import Image

def draw_ui_bounding_boxes(
    pixels: np.ndarray,
    elements: List[Dict],
    output_path: Optional[str] = None,
    show_labels: bool = True
) -> np.ndarray:
    """
    Draws bounding boxes over UI elements on a raw pixel image.
    
    Args:
        pixels (np.ndarray): The image as a NumPy RGB array.
        elements (List[Dict]): List of elements with 'boundingBox' and optional 'text' or 'tag'.
        output_path (str, optional): If specified, saves the annotated image to this path.
        show_labels (bool): Whether to overlay text labels from elements.
    
    Returns:
        np.ndarray: The annotated image.
    """

    if pixels is None or not isinstance(pixels, np.ndarray):
        raise ValueError("❌ 'pixels' must be a valid NumPy RGB image array.")

    annotated = pixels.copy()

    for idx, elem in enumerate(elements):
        box = elem.get("boundingBox")
        if not box:
            continue

        # Extract coordinates
        x = int(box.get("x", 0))
        y = int(box.get("y", 0))
        w = int(box.get("width", 0))
        h = int(box.get("height", 0))

        # Draw bounding box in green
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if show_labels:
            label = elem.get("text") or elem.get("tag") or f"#{idx}"
            label = str(label).strip()

            # Label background
            cv2.rectangle(annotated, (x, y - 20), (x + w, y), (0, 255, 0), -1)
            # Label text
            cv2.putText(
                annotated,
                label,
                (x + 3, y - 5),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 0, 0),
                thickness=1,
                lineType=cv2.LINE_AA
            )

    if output_path:
        try:
            Image.fromarray(annotated).save(output_path)
            print(f"[Visualizer] 🖼️ Annotated image saved to: {output_path}")
        except Exception as e:
            print(f"[Visualizer] ❌ Failed to save annotated image: {e}")

    return annotated
