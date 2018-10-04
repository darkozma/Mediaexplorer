# -*- coding: utf-8 -*-
from core.libs import *

services = {
    "OnlineUpToBox": 'http://uptobox.com/%s',
    "OnlineYourUpload": 'https://www.yourupload.com/watch/%s',
    "TheVideoMe": 'https://thevideo.me/embed-%s.html',
    "OnlineFilesCDN": 'http://filescdn.com/%s',
    "OnlineGD": 'http://www.cinecalidad.to/protect/gdredirect.php?l=%s',
    "OnlineUsersCloud": 'http://userscloud.com/%s',
    "OnlineUsersFiles": 'http://usersfiles.com/%s',
    'OnlineOkRu': 'http://ok.ru/video/%s',
    "OnlineOpenload": 'https://openload.co/f/%s',
    "OnlineStreamango": "http://streamango.com/embed/%s",
    "OnlineRapidVideo": "https://www.rapidvideo.com/e/%s",
    "UploadedTo": 'http://uploaded.net/file/%s',
    "TurboBit": 'http://turbobit.net/%s.html',
    "Mega": 'http://www.cinecalidad.to/protect/v.html?i=%s',
    "BitTorrent": 'http://www.cinecalidad.to/protect/v.html?i=%s',
    "MediaFire": 'http://www.cinecalidad.to/protect/v.html?i=%s',
    "Trailer": 'https://www.youtube.com/watch?v=%s',
    "OnlineMega": "https://mega.nz/#!%s"
}


def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Novedades',
        action='movies',
        content_type='movies',
        url='http://www.cinecalidad.to/espana/'
    ))

    itemlist.append(item.clone(
        label='Destacadas',
        action='movies',
        content_type='movies',
        url='http://www.cinecalidad.to/espana/genero-peliculas/destacada/'
    ))

    itemlist.append(item.clone(
        label='Generos',
        action='categorias',
        content_type='items',
        url='http://www.cinecalidad.to/espana/'
    ))

    itemlist.append(item.clone(
        label='Buscar',
        action='search',
        content_type='movies',
        query=True,
        type='search'
    ))

    return itemlist


def search(item):
    logger.trace()
    item.url = 'http://www.cinecalidad.to/espana/?s=%s' % item.query
    return movies(item)


def categorias(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    patron = '<li id="menu-item-[^"]+" class="menu-item menu-item-type-taxonomy' \
             ' menu-item-object-category menu-item-[^"]+">' \
             '<a href="(?P<url>[^"]+)">(?P<label>[^<]+)</a></li>'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            action='movies',
            label=result.group('label').strip(),
            url=result.group('url'),
            content_type='movies'
        ))

    return itemlist


def movies(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    patron = '<div class="home_post_cont[^"]+">\s+<a href="(?P<url>[^"]+)".*?' \
             'src="(?P<poster>[^"]+)".*?title="(?P<title>[^"]+)(?P<year>\([\d]+\))".*?' \
             '<p>(?P<plot>[^<]+)</p>'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            action='findvideos',
            title=result.group('title').strip(),
            url=result.group('url'),
            poster=result.group('poster'),
            type='movie',
            content_type='servers',
            plot=result.group('plot'),
            year=result.group('year').strip('()')
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data, "<link rel='next' href='([^']+)' />")
    if next_url:
        itemlist.append(item.clone(
            action='movies',
            url=next_url,
            type='next'
        ))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    patron = '<a.*?service="(?P<service>[^"]+)".*?data="(?P<data>[\d\s]+)"><li>' \
             '(?P<server>[^"<]+)</li>(?:</a><div class="anotacion_link"[^>]*>(?P<quality>[^<]+))?'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        url = get_server_url(result.group('data'), result.group('service'))
        if url:
            if 'http://www.cinecalidad.to/protect/' in url:
                data = httptools.downloadpage(
                    'http://www.cinecalidad.to/protect/contenido.php?i=%s' % url.split('=')[1],
                ).data

                url = scrapertools.find_single_match(data, 'href="([^"]+)"')

            itemlist.append(item.clone(
                action='play',
                url=url,
                type='server'
            ))

    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist


def get_server_url(video_id, service_id):
    logger.trace()
    video_id = ''.join(map(chr, [int(x) - 4 for x in video_id.split(' ')]))
    try:
        return services[service_id] % video_id
    except KeyError:
        logger.debug("service %s no encontrado" % service_id)
        return None