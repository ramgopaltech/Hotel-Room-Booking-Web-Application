import os
from PIL import Image, ImageDraw, ImageFont

images_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(images_dir, exist_ok=True)

image_specs = [
    ('hero_bg.jpg', (1600, 900), (12, 16, 24), (40, 50, 70), 'GRAND ROYALE MONACO', 'ULTIMATE LUXURY SANCTUARY'),
    ('about_hotel.jpg', (1200, 800), (20, 25, 35), (60, 75, 100), 'GRAND ROYALE PALACE', 'ESTABLISHED 1974'),
    ('room_penthouse.jpg', (1000, 700), (25, 20, 35), (100, 70, 120), 'ROYAL IMPERIAL SUITE', 'PENTHOUSE • OCEAN VIEW'),
    ('room_penthouse_2.jpg', (1000, 700), (30, 22, 40), (120, 80, 140), 'ROYAL IMPERIAL JACUZZI', 'PRIVATE MARBLE BATH'),
    ('room_penthouse_3.jpg', (1000, 700), (20, 18, 30), (80, 60, 100), 'TERRACE LOUNGE', 'PANORAMIC SUNSET VIEW'),
    ('room_ocean.jpg', (1000, 700), (15, 35, 45), (40, 100, 130), 'GRAND OCEANFRONT VILLA', 'SAPPHIRE BAY VIEW'),
    ('room_ocean_2.jpg', (1000, 700), (20, 40, 55), (50, 110, 145), 'PRIVATE BALCONY', 'INFINITY HORIZON'),
    ('room_executive.jpg', (1000, 700), (30, 35, 30), (80, 95, 80), 'EXECUTIVE SKYLINE SUITE', 'ERGONOMIC STUDIO & CLUB'),
    ('room_deluxe.jpg', (1000, 700), (40, 30, 25), (120, 90, 70), 'DELUXE GARDEN HAVEN', 'BOTANICAL SANCTUARY'),
    ('room_classic.jpg', (1000, 700), (35, 35, 40), (90, 90, 110), 'CLASSIC ELEGANCE ROOM', 'KING BED & ENTERTAINMENT'),
    ('room_presidential.jpg', (1000, 700), (45, 35, 15), (140, 110, 50), 'PRESIDENTIAL SANCTUARY', '2,500 SQ FT • PLUNGE POOL')
]

def generate_luxury_image(filename, size, color1, color2, title, subtitle):
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    # Vertical gradient
    width, height = size
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * (y / height))
        g = int(color1[1] + (color2[1] - color1[1]) * (y / height))
        b = int(color1[2] + (color2[2] - color1[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add geometric luxury pattern accent lines
    gold = (212, 175, 55)
    gold_dim = (120, 100, 35)

    # Outer border frame
    draw.rectangle([30, 30, width - 30, height - 30], outline=gold_dim, width=2)
    draw.rectangle([45, 45, width - 45, height - 45], outline=gold, width=1)

    # Title & Subtitle text placement
    try:
        font_title = ImageFont.truetype("arial.ttf", int(height / 14))
        font_sub = ImageFont.truetype("arial.ttf", int(height / 24))
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw Title
    tb = draw.textbbox((0, 0), title, font=font_title)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    draw.text(((width - tw) / 2, (height - th) / 2 - 20), title, fill=(255, 255, 255), font=font_title)

    # Draw Subtitle
    sb = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    draw.text(((width - sw) / 2, (height - sh) / 2 + 40), subtitle, fill=gold, font=font_sub)

    filepath = os.path.join(images_dir, filename)
    img.save(filepath, quality=95)
    print(f"Generated seed image: {filename}")

for spec in image_specs:
    generate_luxury_image(*spec)

print("All luxury seed images generated successfully!")
