from PIL import Image, ImageDraw, ImageFont
from bahire_hasab import BahireHasab


def _bh(year: int):
    bh = BahireHasab(year)
    table = f"""
    ዓመተ ምህረት፡      {year}
    
    ወንጌላዊ፡ 
    
    እንቁጣጣሸ፡

    ጾመ ነነዌ፡

    ዓቢይ ጾም፡

    ደብረ ዘይት፡

    ሆሳዕና፡

    ስቅለት፡

    ትንሳኤ፡

    እርገት፡

    ጰራቅሊጦስ፡

    ጾመ ሐዋርያት፡

    ጾመ ድህነት፡

    """
    img = Image.open("images/bahire-hasab-bg.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/zelan.ttf", size=45)
    draw.text((100, 100), table, (0, 0, 0), font=font)
    img.show()


_bh(2015)
