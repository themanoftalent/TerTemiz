import os
from PIL import Image, ImageDraw, ImageFont

def generate_tertemiz_logo():
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = (256, 256)
    radius = 230

    # Modern vibrant gradient circle: TerTemiz Emerald & Ocean Blue or Vibrant Orange-Red
    # TerTemiz signature: deep energetic orange/amber (#FF5722 -> #FF9800) with clean cyan sparks
    for r in range(radius, 0, -1):
        ratio = r / radius
        r_col = int(245 * ratio + 225 * (1 - ratio))
        g_col = int(75 * ratio + 40 * (1 - ratio))
        b_col = int(25 * ratio + 20 * (1 - ratio))
        draw.ellipse(
            [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
            fill=(r_col, g_col, b_col, 255)
        )

    # Highlight ring
    draw.ellipse([36, 36, 476, 476], outline=(255, 140, 80, 110), width=6)

    # Draw bold, sleek Letter "T" for TerTemiz
    # Horizontal top bar: [130, 110, 382, 180]
    draw.rounded_rectangle([130, 110, 382, 175], radius=16, fill=(255, 255, 255, 255))
    # Vertical stem: [222, 175, 290, 400]
    draw.rounded_rectangle([222, 175, 290, 395], radius=16, fill=(255, 255, 255, 255))

    # Broom / brush sweeping across the bottom right of the "T"
    brush_mask = Image.new("RGBA", size, (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(brush_mask)

    # Handle (wooden gold)
    b_draw.line([(240, 300), (395, 410)], fill=(130, 85, 30, 255), width=22)
    # Silver ferrule
    b_draw.line([(325, 360), (360, 385)], fill=(210, 220, 235, 255), width=28)
    # Yellow broom bristles
    bristles_poly = [(355, 370), (450, 425), (420, 465), (330, 395)]
    b_draw.polygon(bristles_poly, fill=(255, 200, 30, 255))
    # Bristle texture
    for off in range(-25, 30, 7):
        b_draw.line([(345 + off//2, 380 - off//2), (435 + off, 445 - off//2)], fill=(220, 155, 10, 255), width=3)

    # Sparkle stars in top right (indicating "TerTemiz" sparkling cleanliness)
    sparkle_color = (255, 255, 255, 240)
    # 4-point star at (400, 130)
    b_draw.polygon([(400, 105), (405, 125), (425, 130), (405, 135), (400, 155), (395, 135), (375, 130), (395, 125)], fill=sparkle_color)
    # Small star at (110, 190)
    b_draw.polygon([(110, 175), (113, 187), (125, 190), (113, 193), (110, 205), (107, 193), (95, 190), (107, 187)], fill=sparkle_color)

    img.alpha_composite(brush_mask)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    png_path = os.path.join(assets_dir, "tertemiz_logo.png")
    ico_path = os.path.join(assets_dir, "tertemiz_icon.ico")
    img.save(png_path, "PNG")

    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)

    # Also overwrite the previous ccleaner filenames as aliases
    img.save(os.path.join(assets_dir, "ccleaner_logo.png"), "PNG")
    img.save(os.path.join(assets_dir, "ccleaner_icon.ico"), format="ICO", sizes=icon_sizes)

    print("TerTemiz assets generated successfully:", png_path, ico_path)

if __name__ == "__main__":
    generate_tertemiz_logo()
