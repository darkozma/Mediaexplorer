# -*- coding: utf-8 -*-

import js2py
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = []

    referer = item.url.replace('iframe', 'preview')

    data = httptools.downloadpage(item.url, headers={'referer': referer}).data

    if data == "File was deleted" in data:
        return "El archivo no existe o ha sido borrado"

    unpacked = js2py.eval_js(
        scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>eval(.*?)</script>"))

    url = scrapertools.find_single_match(unpacked, "src:'([^']+\.mp4)")
    script = scrapertools.find_multiple_matches(data, '(var _[0-9a-z]+=.*?\n)')[1]
    script=re.compile("(_[0-9a-z]+)=\$(\[[^\]]+])\(_[0-9a-z]+,", re.IGNORECASE).sub(
        lambda x: x.group(1) + '=' + x.group(1) + x.group(2) + '(', script)

    url = js2py.eval_js(script + "var source = new Array ({'file':'%s'}); var size = source.size(); source[0]['file'];" % url)

    itemlist.append(Video(url=url))

    return itemlist
