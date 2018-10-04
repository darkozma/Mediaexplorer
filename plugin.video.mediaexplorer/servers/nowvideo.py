# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if 'The file is being converted' in data:
        return 'El fichero está en proceso'
    elif 'no longer exists' in data:
        return 'El fichero ha sido borrado'
        
    urls = scrapertools.find_multiple_matches(data, '<source src=[\'"]([^\'"]+)[\'"]')

    for url in urls:
        itemlist.append(Video(url=url, headers = {'User-Agent': httptools.default_headers["User-Agent"]}))

    return itemlist
