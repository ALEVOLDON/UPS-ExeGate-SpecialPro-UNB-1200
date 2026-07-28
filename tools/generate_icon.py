import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def generate_ups_icon():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")
    static_dir = os.path.join(base_dir, "app", "static")
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)

    size = 512
    # Supersampling 2x for ultra smooth antialiasing
    scale = 2
    canvas_size = size * scale
    
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = canvas_size / 2
    r_outer = 230 * scale
    r_inner = 200 * scale

    # Outer glow / background circle
    # Dark slate blue background with glowing emerald-cyan border
    draw.ellipse(
        [center - r_outer, center - r_outer, center + r_outer, center + r_outer],
        fill=(15, 23, 42, 255),
        outline=(16, 185, 129, 255),
        width=16 * scale
    )

    # Inner subtle ring
    draw.ellipse(
        [center - r_inner, center - r_inner, center + r_inner, center + r_inner],
        outline=(6, 182, 212, 160),
        width=6 * scale
    )

    # Battery shape outline
    # Battery body: x1, y1, x2, y2
    bx1, by1 = center - 110 * scale, center - 130 * scale
    bx2, by2 = center + 110 * scale, center + 140 * scale
    radius = 24 * scale

    # Rounded rectangle for battery
    draw.rounded_rectangle(
        [bx1, by1, bx2, by2],
        radius=radius,
        fill=(30, 41, 59, 255),
        outline=(16, 185, 129, 255),
        width=12 * scale
    )

    # Battery cap at top
    cap_w = 70 * scale
    cap_h = 22 * scale
    draw.rounded_rectangle(
        [center - cap_w/2, by1 - cap_h, center + cap_w/2, by1],
        radius=8 * scale,
        fill=(16, 185, 129, 255)
    )

    # Battery charge bars inside (bottom to top)
    bar_margin_x = 20 * scale
    bar_h = 36 * scale
    gap = 12 * scale
    
    # 3 green bars inside battery
    for i in range(3):
        bar_y2 = by2 - 20 * scale - i * (bar_h + gap)
        bar_y1 = bar_y2 - bar_h
        draw.rounded_rectangle(
            [bx1 + bar_margin_x, bar_y1, bx2 - bar_margin_x, bar_y2],
            radius=6 * scale,
            fill=(16, 185, 129, 210)
        )

    # Sharp Glowing Lightning Bolt Overlay in center
    # Centered lightning bolt coordinates
    bolt_points = [
        (center + 20 * scale, center - 160 * scale),
        (center - 70 * scale, center + 10 * scale),
        (center - 10 * scale, center + 10 * scale),
        (center - 30 * scale, center + 170 * scale),
        (center + 70 * scale, center - 10 * scale),
        (center + 10 * scale, center - 10 * scale),
    ]

    # Draw bolt shadow for glow effect
    glow_img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.polygon(bolt_points, fill=(245, 158, 11, 255))
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=15 * scale))
    
    img = Image.alpha_composite(img, glow_img)
    draw = ImageDraw.Draw(img)

    # Draw main lightning bolt (Yellow to Gold)
    draw.polygon(bolt_points, fill=(255, 215, 0, 255), outline=(255, 255, 255, 255), width=4 * scale)

    # Downsample back to 512x512 with high quality LANCZOS
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Save PNG assets
    ico_png_path = os.path.join(assets_dir, "app_icon.png")
    final_img.save(ico_png_path, format="PNG")
    print(f"[+] Saved PNG icon to: {ico_png_path}")

    static_png_path = os.path.join(static_dir, "favicon.png")
    final_img.save(static_png_path, format="PNG")

    # Save ICO assets (multi-size for crisp rendering at 16x16 up to 256x256)
    ico_asset_path = os.path.join(assets_dir, "app_icon.ico")
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    final_img.save(ico_asset_path, format="ICO", sizes=sizes)
    print(f"[+] Saved ICO icon to: {ico_asset_path}")

    static_ico_path = os.path.join(static_dir, "favicon.ico")
    final_img.save(static_ico_path, format="ICO", sizes=sizes)
    print(f"[+] Saved Favicon ICO to: {static_ico_path}")

if __name__ == "__main__":
    generate_ups_icon()
