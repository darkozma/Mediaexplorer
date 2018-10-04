# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    if "Page not found" in data or "File was deleted" in data:
        return "El archivo no existe o ha sido borrado"

    if "Video is processing now" in data:
        return "El vídeo se está procesando"

    for url, res in scrapertools.find_multiple_matches(data, 'src:\s*"([^"]+)".*?res:\s*"(\d+)'):
        itemlist.append(Video(url=url, res=res))

    return itemlist
