# -*- coding: utf-8 -*-
from core.libs import *

url_api = settings.get_setting('url_api', __file__)
beeg_salt = settings.get_setting('beeg_salt', __file__)


def get_api_url():
    logger.trace()

    global url_api
    global beeg_salt

    data = httptools.downloadpage('http://beeg.com').data
    version = re.compile('<script src="/static/cpl/([\d]+).js"').findall(data)[0]

    js_url = 'https://beeg.com/static/cpl/%s.js' % version
    url_api = 'https://beeg.com/api/v6/' + version

    data = httptools.downloadpage(js_url).data
    beeg_salt = re.compile('beeg_salt="([^"]+)"').findall(data)[0]

    settings.set_setting('url_api', url_api, __file__)
    settings.set_setting('beeg_salt', beeg_salt, __file__)


def decode(key):
    a = beeg_salt
    e = unicode(urllib.unquote(key), 'utf8')
    t = len(a)
    o = ''
    for n in range(len(e)):
        r = ord(e[n:n + 1])
        i = n % t
        s = ord(a[i:i + 1]) % 21
        o += chr(r - s)

    n = []
    for x in range(len(o), 0, -3):
        if x >= 3:
            n.append(o[(x - 3):x])
        else:
            n.append(o[0:x])

    return ''.join(n)


def mainlist(item):
    logger.trace()
    get_api_url()
    itemlist = list()

    itemlist.append(item.clone(
        action='videos',
        label='Útimos videos',
        url=url_api + '/index/main/0/pc',
        content_type='videos'
    ))

    itemlist.append(item.clone(
        action='listcategorias',
        label='Listado categorias',
        url=url_api + '/index/main/0/pc',
        content_type='items'
    ))

    itemlist.append(item.clone(
        action='search',
        label='Buscar',
        content_type='items',
        category='adult',
        query=True
    ))

    return itemlist


def videos(item):
    logger.trace()
    itemlist = list()

    json_data = jsontools.load_json(httptools.downloadpage(item.url).data)

    for video in json_data['videos']:
        itemlist.append(item.clone(
            action='play',
            title=video['title'],
            url=url_api + '/video/' + video['id'],
            thumb='http://img.beeg.com/236x177/' + video['id'] + '.jpg',
            folder=True,
            type='video'
        ))

    page = int(scrapertools.find_single_match(item.url, url_api + '/index/[^/]+/([0-9]+)/pc'))

    if json_data['pages'] - 1 > page:
        itemlist.append(item.clone(
            action='videos',
            url=item.url.replace('/' + str(page) + '/', '/' + str(page + 1) + '/'),
            type='next'
        ))

    return itemlist


def listcategorias(item):
    logger.trace()
    itemlist = list()

    json_data = jsontools.load_json(httptools.downloadpage(item.url).data)

    for tag in json_data['tags']:
        itemlist.append(item.clone(
            action='videos',
            label=tag['tag'].capitalize(),
            url=url_api + '/index/tag/0/pc?tag=' + tag['tag'],
            content_type='videos',
            type='item'
        ))

    return itemlist


def search(item):
    logger.trace()
    itemlist = list()

    item.url = url_api + '/suggest?q=%s' % item.query
    json_data = jsontools.load_json(httptools.downloadpage(item.url).data)

    for tag in json_data['items']:
        itemlist.append(item.clone(
            action='videos',
            label=tag['name'].capitalize(),
            url=url_api + '/index/tag/0/pc?tag=' + tag['name'],
            content_type='videos',
            type='item'
        ))

    return itemlist


def play(item):
    logger.trace()
    itemlist = list()

    json_data = jsontools.load_json(httptools.downloadpage(item.url).data)

    for key in json_data:
        video_list = re.compile('([0-9]+p)', re.DOTALL).findall(key)
        if video_list:
            video = video_list[0]
            if json_data[video] is not None:
                url = json_data[video]
                url = url.replace('{DATA_MARKERS}', 'data=pc.ES')
                viedokey = re.compile('key=(.*?)%2Cend=', re.DOTALL).findall(url)[0]

                url = url.replace(viedokey, decode(viedokey))
                if not url.startswith('https:'):
                    url = 'https:' + url

                itemlist.append(Video(url=url, res=video))

    return sorted(itemlist, key=lambda x: int(x.res[:-1]) if x.res else 0, reverse=True)
