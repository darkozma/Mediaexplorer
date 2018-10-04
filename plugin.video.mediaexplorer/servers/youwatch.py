# -*- coding: utf-8 -*-
from core.libs import *

def get_video_url(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    
    if "File Not Found" in data:
        return "El archivo no existe o ha sido borrado"
       
    url = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url).data
    
    if "We're sorry, this video is no longer available" in data:
        return "El archivo no existe o ha sido borrado"

        
    url = scrapertools.get_match(data, '{file:"([^"]+)"')
    itemlist.append(Video(url=url))

    return itemlist
