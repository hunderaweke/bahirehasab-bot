from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def draw_post_card(sender_name: str, reciever_name: str, template_name: str):
    if template_name == "images/template-1.png":
        color = (109, 46, 0)
    elif template_name == "images/template-2.png":
        color = (255, 227, 80)
    img = Image.open(template_name)
    bio = BytesIO()
    bio.name = "drawn-template.png"
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/noto.ttf", size=25)
    draw.text((201, 63), sender_name, color, font=font)
    draw.text((490, 337), reciever_name, color, font=font)
    img.save(bio, "PNG")
    bio.seek(0)
    return bio
