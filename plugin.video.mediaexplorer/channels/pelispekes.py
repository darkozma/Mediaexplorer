# -*- coding: utf-8 -*-
from core.libs import *

LNG = Languages({
    Languages.es: ["Español"],
    Languages.la: ["Latino"],
    Languages.sub_es: ["Subtitulado"]

})


def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        action='videos',
        label='Novedades',
        content_type='movies',
        url='http://www.pelispekes.com'
    ))

    itemlist.append(item.clone(
        action='categories',
        label='Categorias',
        content_type='items'
    ))

    itemlist.append(item.clone(
        action='search',
        label='Buscar...',
        content_type='movies',
        category='child',
        type='search',
        query=True
    ))

    return itemlist


def search(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url or 'http://www.pelispekes.com/?s=%s' % item.query).data

    patron = '<a href="(?P<url>[^"]+)" title="(?P<title>[^"]+)">[^<]+' \
             '<img src="(?P<thumb>[^"]+)".*?' \
             '<p class="main-info-list">[^<]+(?P<year>\d+)</p>.*?' \
             '<p class="text-list">(?P<plot>[^<]+)</p>.*?' \
             '<div class="list-score">(?P<rat>[^<]+)</div>'

    for match in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            action="findvideos",
            title=match.group('title'),
            url=match.group('url'),
            poster=match.group('thumb'),
            type='movie',
            content_type='servers'
        ))

    # Extrae la pagina siguiente
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right')
    if next_page:
        itemlist.append(item.clone(
            url=next_page,
            type='next'
        ))

    return itemlist


def categories(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage('http://www.pelispekes.com').data

    pattern = '<li class="[^"]+"><a href="(?P<url>[^"]+)">(?P<label>[^<]+)</a></li>'

    for match in re.compile(pattern, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            action="videos",
            label=match.group('label').capitalize(),
            url=match.group('url'),
            type='item',
            content_type='movies'
        ))

    return sorted(itemlist, key=lambda x: x.label)


def videos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    patron = '<div class="col-mt-5 postsh">.*?<a href="(?P<url>[^"]+)" ' \
             'title="(?P<title>[^"]+)".*?"' \
             'rating-number">(?P<rat>[^<]+)</span>.*?' \
             'src="(?P<thumb>[^"]+)'

    for match in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            action="findvideos",
            title=match.group('title'),
            url=match.group('url'),
            poster=match.group('thumb'),
            type='movie',
            content_type='servers'
        ))

    # Extrae la pagina siguiente
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right')
    if next_page:
        itemlist.append(item.clone(
            url=next_page,
            type='next'
        ))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()
    # Descarga la página para obtener el argumento
    data = httptools.downloadpage(item.url).data

    item.plot = scrapertools.find_single_match(data, '<h2>Sinopsis</h2><p>(.*?)</p><div')

    pattern = '<a href="#(?P<id>reprox[^"]+)".*?</span>\n(?P<lang>[^<]+)\n</a>'
    langs = dict([(match.group('id'), match.group('lang')) for match in re.compile(pattern, re.DOTALL).finditer(data)])

    pattern = '<div class="tab-pane reproductor repron" id="(?P<id>[^"]+)".*?<iframe.*?src="(?P<url>[^"]+)"'

    for match in re.compile(pattern, re.DOTALL).finditer(data):
        url = match.group('url').replace("www.pelispekes.com/player/tune.php?nt=", "netu.tv/watch_video.php?v=")
        itemlist.append(item.clone(
            url=url,
            type='server',
            lang=LNG.get(langs[match.group('id')])
        ))

    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist
