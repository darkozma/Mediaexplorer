# -*- coding: utf-8 -*-

from core.libs import *
import js2py


def get_video_url(item):
    logger.trace()
    itemlist = []

    referer = re.sub(r"embed-|player-", "", item.url)[:-5]

    data = httptools.downloadpage(item.url, headers={'Referer': referer}).data

    if data == "File was deleted":
        return "El archivo no existe o ha sido borrado"

    unpacked = js2py.eval_js(
        scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>eval(.*?)</script>"))

    url = scrapertools.find_single_match(unpacked, '(http[^,]+\.mp4)')
    script = scrapertools.find_single_match(data, '(var _[0-9a-z]+=.*?\n)')
    script = re.compile("(_[0-9a-z]+)=\$(\[[^\]]+])\(_[0-9a-z]+,", re.IGNORECASE).sub(
        lambda x: x.group(1) + '=' + x.group(1) + x.group(2) + '(', script)

    url = js2py.eval_js(script + "var source = new Array ('%s'); source.size()[0];" % url)

    itemlist.append(Video(url=url))

    return itemlist
