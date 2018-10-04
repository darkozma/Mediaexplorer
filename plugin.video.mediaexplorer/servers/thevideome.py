# -*- coding: utf-8 -*-
from core.libs import *

def get_video_url(item):
    logger.trace()
    itemlist = []

    if not "embed" in item.url:
        item.url = 'https://thevideo.website/embed-' + item.url.rsplit('/',1)[1] + '.html'

    data = httptools.downloadpage(item.url).data

    if "File was deleted" in data or "Page Cannot Be Found" in data:
        return "El archivo ha sido eliminado o no existe"

    var = scrapertools.find_single_match(data, 'vsign.player.*?\+ (\w+)')
    mpri_Key = scrapertools.find_single_match(data, "%s='([^']+)'" % var)
    data_vt = httptools.downloadpage("https://thevideo.me/vsign/player/%s" % mpri_Key).data
    vt = scrapertools.find_single_match(data_vt, 'function\|([^\|]+)\|')
    if "fallback" in vt:
        vt = scrapertools.find_single_match(data_vt, 'jwConfig\|([^\|]+)\|')

    matches = scrapertools.find_multiple_matches(data, '\{"file"\s*\:\s*"([^"]+)"\s*,\s*"label"\s*\:\s*"([^"]+)"')

    for url, label in matches:
        url += "?direct=false&ua=1&vt=%s" % vt
        itemlist.append(Video(url=url, res=label))
        
    return itemlist