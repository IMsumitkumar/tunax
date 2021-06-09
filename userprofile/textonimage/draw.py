from PIL import Image, ImageFont, ImageDraw
from django.conf import settings


def make_certificate(image_name: str, data_dict: dict):
    media_root = settings.MEDIA_ROOT
    image = str(media_root) + '/certificate/'+ image_name

    title_text = "hello world"
    # title_font = ImageFont.truetype("BLKCHCRY.TTF", 20)
    img = Image.open(str(image)).convert('RGB')
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), title_text, fill=(1, 1, 1))

    tournament_name = data_dict.get("tournament_name")
    team_owner = data_dict.get("team_owner")
    img.save(f"{media_root}/certificate/certificate-{team_owner}-{tournament_name}.jpg")

    return f"{media_root}/certificate/certificate-{team_owner}-{tournament_name}.jpg"