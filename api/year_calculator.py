from PIL import Image, ImageDraw, ImageColor
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
