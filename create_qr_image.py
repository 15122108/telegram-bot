from pathlib import Path

from PIL import Image, ImageDraw


QR_LINK = "https://mobile.nbu.uz/qr/ZXlKcFpDSTZOVE0xT0RZM01Td2lkSGx3WlNJNkltTmhjbVFpZlE9PQ"
OUT = Path(__file__).with_name("payment_qr.png")


def main() -> None:
    try:
        import qrcode
    except ImportError as exc:
        raise SystemExit("qrcode package is required to generate this asset") from exc

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=3,
    )
    qr.add_data(QR_LINK)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#063b75", back_color="#ffffff").convert("RGB")

    canvas = Image.new("RGB", (image.width + 96, image.height + 150), "#ffffff")
    canvas.paste(image, (48, 48))

    draw = ImageDraw.Draw(canvas)
    draw.text((48, image.height + 70), "NBU QR payment", fill="#063b75")
    draw.text((48, image.height + 100), "Scan to pay for your eSIM order", fill="#233044")

    canvas.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()

