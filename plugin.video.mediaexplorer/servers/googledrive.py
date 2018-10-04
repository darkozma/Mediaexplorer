# -*- coding: utf-8 -*-
# TODO: No consigo que se reproduzcan los videos, a pesar que la url parece ser correcta ya que vlc la reproduce sin
# TODO: problemas, pero algo falla con kodi (por lo menos a mi) que no es capaz de reproducirlo pendiente de probar en
# TODO: otros dispositivos
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data,'href="(/uc\?export=download&confirm=[^&]+&id=[^"]+)"')
    url = httptools.downloadpage(urlparse.urljoin(item.url, url), follow_redirects=False).headers['location']

    filename = httptools.downloadpage(url, only_headers=True, follow_redirects=False).headers['content-disposition']
    ext = scrapertools.find_single_match(filename, 'filename="[^"]+\.([^".]+)"')

    itemlist.append(Video(url=url, type=ext))

    return itemlist
