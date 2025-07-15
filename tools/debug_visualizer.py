from PIL import Image, ImageDraw, ImageFont
import os

def draw_button_overlay(pixel_array, elements, output_path):
    img = Image.fromarray(pixel_array.astype("uint8"), "RGB")
    draw = ImageDraw.Draw(img)

    # Load a font (fallback to default if not available)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()

    for el in elements:
        label = el.get("label", "unknown")
        conf = el.get("confidence", 0)
        ctx = el.get("context", "")
        annotation = f"{label} ({conf:.2f}) {ctx}"

        # Draw bounding box if present
        if all(k in el for k in ["x_min", "y_min", "x_max", "y_max"]):
            box = (el["x_min"], el["y_min"], el["x_max"], el["y_max"])
            draw.rectangle(box, outline="red", width=2)
            draw.text((box[0] + 2, box[1] - 12), annotation, fill="yellow", font=font)
        elif "x" in el and "y" in el:
            x, y = el["x"], el["y"]
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="red")
            draw.text((x + 8, y - 8), annotation, fill="yellow", font=font)

    img.save(output_path)
    print(f"[Visualizer] 🖼️ Saved debug overlay: {output_path}")
