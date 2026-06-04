from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


SIZE = 1024
OUT = Path(__file__).with_name("visa_esim_bot_profile.png")


def rounded_rectangle(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def main():
    image = Image.new("RGB", (SIZE, SIZE), "#0b1726")
    draw = ImageDraw.Draw(image)

    # Soft radial background.
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((-180, -160, 760, 760), fill=(0, 195, 165, 120))
    glow_draw.ellipse((320, 220, 1220, 1120), fill=(47, 116, 255, 125))
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    image = Image.alpha_composite(image.convert("RGBA"), glow)
    draw = ImageDraw.Draw(image)

    # Outer ring.
    draw.ellipse((92, 92, 932, 932), outline=(255, 255, 255, 42), width=8)
    draw.ellipse((128, 128, 896, 896), outline=(0, 226, 196, 95), width=5)

    # Passport.
    passport = (230, 220, 610, 770)
    rounded_rectangle(draw, passport, 46, fill="#174a8b", outline="#75d9ff", width=8)
    rounded_rectangle(draw, (270, 274, 570, 716), 28, fill="#123d76", outline="#2b80d7", width=3)

    # Passport globe.
    draw.ellipse((330, 372, 510, 552), outline="#d7f7ff", width=10)
    draw.arc((356, 372, 484, 552), 78, 282, fill="#d7f7ff", width=7)
    draw.arc((356, 372, 484, 552), -102, 102, fill="#d7f7ff", width=7)
    draw.line((330, 462, 510, 462), fill="#d7f7ff", width=7)
    draw.line((420, 374, 420, 550), fill="#d7f7ff", width=7)

    # Visa stamp.
    draw.rounded_rectangle((312, 596, 530, 670), radius=18, fill="#ffffff", outline="#b8f7ff", width=4)
    draw.line((344, 634, 498, 634), fill="#1d65b7", width=8)
    draw.line((374, 612, 468, 612), fill="#1d65b7", width=7)
    draw.line((374, 656, 468, 656), fill="#1d65b7", width=7)

    # eSIM chip card.
    chip = (472, 404, 798, 728)
    rounded_rectangle(draw, chip, 58, fill="#f7fbff", outline="#ffffff", width=9)
    rounded_rectangle(draw, (532, 468, 738, 666), 28, fill="#12c7a8", outline="#0b846e", width=7)

    # Chip contacts.
    contact = "#063d45"
    draw.line((635, 468, 635, 666), fill=contact, width=8)
    draw.line((532, 566, 738, 566), fill=contact, width=8)
    draw.line((582, 468, 582, 528), fill=contact, width=7)
    draw.line((688, 468, 688, 528), fill=contact, width=7)
    draw.line((582, 606, 582, 666), fill=contact, width=7)
    draw.line((688, 606, 688, 666), fill=contact, width=7)

    # Signal arcs.
    for idx, box in enumerate([(716, 304, 838, 426), (684, 270, 880, 466), (648, 234, 924, 510)]):
        draw.arc(box, -47, 43, fill="#ffffff", width=13 - idx)

    # Uzbekistan-inspired accent stripes.
    draw.arc((158, 158, 866, 866), 218, 310, fill="#ffffff", width=16)
    draw.arc((178, 178, 846, 846), 218, 310, fill="#f04444", width=9)
    draw.arc((198, 198, 826, 826), 218, 310, fill="#19c37d", width=12)

    # Mask to a clean circle for Telegram preview.
    mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((20, 20, SIZE - 20, SIZE - 20), fill=255)
    output = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    output.paste(image, (0, 0), mask)
    output.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()

