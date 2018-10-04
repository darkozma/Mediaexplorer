# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    if "Invalid or Deleted File" in data:
        return "El archivo no existe o ha sido borrado"

    elif "File Removed for Violation" in data:
        return "Archivo eliminado por infracción"

    url = scrapertools.find_single_match(data, 'kNO\s*=\s*"([^"]+)"')
    if url:
        itemlist.append(Video(url=url))

    return itemlist
