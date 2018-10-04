# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if 'Object not found' in data:
        return "El archivo ha sido eliminado o no existe"

    patron = 'https://www.rapidvideo.com/e/([^=]+)=([^"]+)'
    for code, res in scrapertools.find_multiple_matches(data, patron):
        data = httptools.downloadpage('https://www.rapidvideo.com/e/%s=%s' % (code, res)).data
        url = scrapertools.find_single_match(data, 'source src="([^"]+)')
        itemlist.append(Video(url=url, res=res, type=url.split('.')[-1]))

    return itemlist
