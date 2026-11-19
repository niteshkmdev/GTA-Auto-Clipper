import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LOGO_REF = r"C:\Users\neham\.gemini\antigravity\brain\34e199d1-3a5c-49c7-8ba0-0d47b527ef84\.user_uploaded\media_1795106710744_e9ca1c42.jpg"
BANNER_REF = r"C:\Users\neham\.gemini\antigravity\brain\34e199d1-3a5c-49c7-8ba0-0d47b527ef84\.user_uploaded\media_1795106818054_035c3022.jpg"
ASSETS_DIR = r"C:\Users\neham\SourceCode\GTA-Auto-Clipper\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_stylized_text(text1, text2, font_size=120, shear_angle=0.22, tracking=2):
    """
    Renders two-part esports typography (e.g. 'Desi' in white, 'Clutch' in hot neon pink)
    with heavy outline, drop shadow, and neon glow.
    """
    scale = 3  # Supersample for ultra crisp edges
    fs = font_size * scale
    font = ImageFont.truetype(r"C:\Windows\Fonts\ariblk.ttf", fs)

    b1 = font.getbbox(text1)
    w1 = b1[2] - b1[0] + int(tracking * scale)
    b2 = font.getbbox(text2)
    w2 = b2[2] - b2[0]
    total_w = w1 + w2
    total_h = max(b1[3] - b1[1], b2[3] - b2[1]) + int(40 * scale)

    pad_x, pad_y = int(60 * scale), int(60 * scale)
    W, H = total_w + pad_x * 2, total_h + pad_y * 2

    # Canvas for text
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x1 = pad_x
    y1 = pad_y - b1[1]
    x2 = x1 + w1
    y2 = pad_y - b2[1]

    # 1. Outer Glow (Electric cyan + hot pink glow)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_radius = int(18 * scale)
    for dx in range(-g_radius, g_radius + 1, int(4 * scale)):
        for dy in range(-g_radius, g_radius + 1, int(4 * scale)):
            if dx*dx + dy*dy <= g_radius*g_radius:
                g_draw.text((x1 + dx, y1 + dy), text1, font=font, fill=(0, 240, 255, 120))
                g_draw.text((x2 + dx, y2 + dy), text2, font=font, fill=(255, 0, 140, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(int(10 * scale)))

    # 2. Heavy Black Bevel / Outline
    outline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(outline)
    o_radius = int(11 * scale)
    for dx in range(-o_radius, o_radius + 1, int(2 * scale)):
        for dy in range(-o_radius, o_radius + 1, int(2 * scale)):
            if dx*dx + dy*dy <= o_radius*o_radius:
                o_draw.text((x1 + dx, y1 + dy), text1 + text2, font=font, fill=(10, 5, 20, 255))

    # 3. Drop Shadow (offset down-right)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.text((x1 + int(8*scale), y1 + int(12*scale)), text1 + text2, font=font, fill=(5, 2, 10, 220))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(4 * scale)))

    # 4. Fill text
    # text1 (Desi): pure crisp white with slight top highlight
    t1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    t1_draw = ImageDraw.Draw(t1)
    t1_draw.text((x1, y1), text1, font=font, fill=(255, 255, 255, 255))

    # text2 (Clutch): vibrant GTA synthwave neon pink
    t2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    t2_draw = ImageDraw.Draw(t2)
    t2_draw.text((x2, y2), text2, font=font, fill=(255, 25, 130, 255))

    # Merge layers
    merged = Image.alpha_composite(glow, shadow)
    merged = Image.alpha_composite(merged, outline)
    merged = Image.alpha_composite(merged, t1)
    merged = Image.alpha_composite(merged, t2)

    # 5. Apply Italic Shear Transform
    # Affine: (1, -shear_angle, x_shift, 0, 1, 0)
    x_shift = int(H * shear_angle * 0.45)
    sheared = merged.transform(
        (W + int(H * shear_angle), H),
        Image.AFFINE,
        (1, -shear_angle, x_shift, 0, 1, 0),
        resample=Image.BICUBIC
    )

    # Crop bounding box of visible alpha
    bbox = sheared.getbbox()
    if bbox:
        sheared = sheared.crop(bbox)

    target_w = int((w1 + w2) / scale * 1.05)
    target_h = int(sheared.height * (target_w / sheared.width))
    return sheared.resize((target_w, target_h), Image.Resampling.LANCZOS)

def build_desiclutch_logo():
    logo_bgr = cv2.imread(LOGO_REF)
    h, w = logo_bgr.shape[:2]

    # Inpaint old text region (y: 380..585, x: 75..945)
    # The infinity loop below is at y: 535..675
    mask = np.zeros((h, w), dtype=np.uint8)
    sub = logo_bgr[380:575, 75:945]
    white = (sub[:,:,0] > 140) & (sub[:,:,1] > 140) & (sub[:,:,2] > 140)
    pink = (sub[:,:,2] > 140) & (sub[:,:,0] > 90) & (sub[:,:,1] < 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
    dilated = cv2.dilate((white | pink).astype(np.uint8), kernel)
    mask[380:575, 75:945] = dilated * 255

    # Don't erase the top of the infinity loop play button
    mask[550:575, 400:620] = 0

    inpainted = cv2.inpaint(logo_bgr, mask, 7, cv2.INPAINT_TELEA)
    inpainted_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)
    base_img = Image.fromarray(inpainted_rgb)

    # Render "DesiClutch"
    text_img = create_stylized_text("Desi", "Clutch", font_size=136, shear_angle=0.20)

    # Position at center x, y around 410..470
    pos_x = (w - text_img.width) // 2
    pos_y = 398

    # Composite onto base
    base_img.paste(text_img, (pos_x, pos_y), text_img)

    out_path = os.path.join(ASSETS_DIR, "desiclutch_logo.png")
    base_img.save(out_path, format="PNG", quality=95)
    print("Generated Logo:", out_path)
    return out_path

def build_desiclutch_banner():
    banner_bgr = cv2.imread(BANNER_REF)
    h, w = banner_bgr.shape[:2]

    # Inpaint old text region on banner (x: 320..760, y: 170..330)
    mask = np.zeros((h, w), dtype=np.uint8)
    sub = banner_bgr[170:330, 320:760]
    white = (sub[:,:,0] > 140) & (sub[:,:,1] > 140) & (sub[:,:,2] > 140)
    pink = (sub[:,:,2] > 140) & (sub[:,:,0] > 90) & (sub[:,:,1] < 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    dilated = cv2.dilate((white | pink).astype(np.uint8), kernel)
    mask[170:330, 320:760] = dilated * 255
    # Keep the infinity loop at y: 260..340
    mask[265:330, 430:650] = 0

    inpainted = cv2.inpaint(banner_bgr, mask, 5, cv2.INPAINT_TELEA)
    inpainted_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)
    base_img = Image.fromarray(inpainted_rgb)

    # Render "DesiClutch" for banner
    text_img = create_stylized_text("Desi", "Clutch", font_size=74, shear_angle=0.18)

    pos_x = (w - text_img.width) // 2 + 10
    pos_y = 188

    base_img.paste(text_img, (pos_x, pos_y), text_img)

    # Save standard resolution
    out_1024 = os.path.join(ASSETS_DIR, "desiclutch_banner_1024x576.png")
    base_img.save(out_1024, format="PNG", quality=95)

    # Save YouTube standard 2560x1440 banner with perfect safe area
    yt_banner = base_img.resize((2560, 1440), Image.Resampling.LANCZOS)
    out_2560 = os.path.join(ASSETS_DIR, "desiclutch_banner_youtube_2560x1440.png")
    yt_banner.save(out_2560, format="PNG", quality=95)

    print("Generated Banner 1024x576:", out_1024)
    print("Generated Banner YouTube 2560x1440:", out_2560)
    return out_2560

if __name__ == "__main__":
    build_desiclutch_logo()
    build_desiclutch_banner()
