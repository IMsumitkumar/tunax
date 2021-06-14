from PIL import Image, ImageFont, ImageDraw
from django.conf import settings


def make_certificate(image_name: str, data_dict: dict):
    media_root = settings.MEDIA_ROOT
    image = str(media_root) + '/certificate/'+ image_name

    img = Image.open(str(image)).convert('RGB')
    draw = ImageDraw.Draw(img)

    draw.text(xy=(1100, 940), text=data_dict.get("team_name"), fill=(0, 137, 209),
            font=ImageFont.truetype("BLKCHCRY.TTF", 220))
    draw.text(xy=(1190, 1380), text=data_dict.get("tournament_name"), fill=(1, 1, 1),
            font=ImageFont.truetype("BLKCHCRY.TTF", 150))
    draw.text(xy=(1550, 1715), text=data_dict.get("position"), fill=(220,20,60),
            font=ImageFont.truetype("BLKCHCRY.TTF", 220))
    draw.text(xy=(2150, 1620), text=data_dict.get("tournament_owner"), fill=(1, 1, 1),
            font=ImageFont.truetype("BLKCHCRY.TTF", 69))
    draw.text(xy=(540, 1620), text="Founder, CEO", fill=(1, 1, 1),
            font=ImageFont.truetype("BLKCHCRY.TTF", 70))

    tournament_name = data_dict.get("tournament_name")
    team_owner = data_dict.get("team_owner")
    img.save(f"{media_root}/certificate/certificate-{team_owner}-{tournament_name}.jpg")

    return f"{media_root}/certificate/certificate-{team_owner}-{tournament_name}.jpg"