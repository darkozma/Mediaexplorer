# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = []

    id = scrapertools.find_single_match(item.url, '[^/]+//[^/]+/[^-=]+(?:-|=)([0-9a-zA-Z]+)')
    data = httptools.downloadpage(item.url).data

    data = jswise(
        scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>\s*;?(eval.*?)</script>"))
    at = scrapertools.find_single_match(data, 'at=([^&]+)')

    data_player = httptools.downloadpage('http://hqq.watch/sec/player/embed_player.php?vid=%s&at=%s' % (id, at)).data
    data1 = jswise(
        scrapertools.find_single_match(data_player, "<script type=[\"']text/javascript[\"']>\s*;?(eval.*?)</script>"))

    data = urllib.unquote(
        ''.join(scrapertools.find_multiple_matches(data_player, 'document.write\(unescape\("([^"]+)"')))
    subtitle = scrapertools.find_single_match(data, 'value="sublangs=Spanish.*?sub=([^&]+)&') or \
               scrapertools.find_single_match(data, 'value="sublangs=English.*?sub=([^&]+)&')

    params = {
        'vid': id,
        'adb': 0,
        'at': at,
        'link_1': scrapertools.find_multiple_matches(data1, 'var[^=]+= "([^"]+)";')[-2],
        'server_1': scrapertools.find_multiple_matches(data1, 'var[^=]+= "([^"]+)";')[-1]
    }

    urls = httptools.downloadpage("http://hqq.watch/player/get_md5.php?%s" % urllib.urlencode(params),
                                  headers={'X-Requested-With': 'XMLHttpRequest'}).data
    urls = jsontools.load_json(urls)

    url = urls["obf_link"].replace("#", "")
    url = unicode(''.join(map(''.join, zip(*[['\\u0'] * (len(url) / 3)] + ([iter(url)] * 3)))),
                  'unicode-escape').encode('utf8')

    itemlist.append(Video(url="https:" + url + ".mp4.m3u8", subtitle=subtitle))
    return itemlist


def jswise(wise):
    ## js2python
    def js_wise(wise):

        w, i, s, e = wise

        v0 = 0
        v1 = 0
        v2 = 0
        v3 = []
        v4 = []

        while True:
            if v0 < 5:
                v4.append(w[v0])
            elif v0 < len(w):
                v3.append(w[v0])
            v0 += 1
            if v1 < 5:
                v4.append(i[v1])
            elif v1 < len(i):
                v3.append(i[v1])
            v1 += 1
            if v2 < 5:
                v4.append(s[v2])
            elif v2 < len(s):
                v3.append(s[v2])
            v2 += 1
            if len(w) + len(i) + len(s) + len(e) == len(v3) + len(v4) + len(e): break

        v5 = "".join(v3)
        v6 = "".join(v4)
        v1 = 0
        v7 = []

        for v0 in range(0, len(v3), 2):
            v8 = -1
            if ord(v6[v1]) % 2: v8 = 1
            v7.append(chr(int(v5[v0:v0 + 2], 36) - v8))
            v1 += 1
            if v1 >= len(v4): v1 = 0
        return "".join(v7)

    ## loop2unobfuscated
    while True:
        wise = re.search("var\s.+?\('([^']+)','([^']+)','([^']+)','([^']+)'\)", wise, re.DOTALL)
        if not wise: break
        ret = wise = js_wise(wise.groups())
    return ret
