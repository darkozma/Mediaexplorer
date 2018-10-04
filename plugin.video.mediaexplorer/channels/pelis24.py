# -*- coding: utf-8 -*-
from core.libs import *
import base64

HOST = 'https://pelis24.is'

LNG = Languages({
    Languages.en: ['Inglés'],
    Languages.es: ['Español'],
    Languages.la: ['Latino'],
    Languages.sub_es: ['Subtitulado']
})

QLT = Qualities({
    Qualities.scr: ['Ts Screener', 'BR-Screener', 'Cam', 'Mala (CAM)', 'Baja (TS)'],
    Qualities.hd: ['HD Rip 720p', 'Alta (HD)'],
    Qualities.hd_full: ['HD Real 1080p'],
    Qualities.rip: ['Dvd Rip']
})


def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        action="newest",
        label="Novedades",
        url=HOST,
        type="item",
        content_type='movies'))

    itemlist.append(item.clone(
        action="contents",
        label="Estrenos",
        url=HOST + "/genero/peliculas-estreno",
        type="item",
        content_type='movies'))

    itemlist.append(item.clone(
        action="contents",
        label="Películas en Español",
        url=HOST + '/pelicula/tag/espanol-castellano/',
        type="item",
        lang=[LNG.es],
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="contents",
        label="Películas en Latino",
        url=HOST + '/pelicula/tag/espanol-latino/',
        type="item",
        lang=[LNG.la],
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="contents",
        label="Películas subtituladas",
        url=HOST + '/pelicula/tag/subtituladas/',
        type="item",
        lang=[LNG.sub_es],
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="years",
        label="Años",
        url=HOST,
        type="item"
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST,
        type="item"
    ))

    itemlist.append(item.clone(
        action="search",
        label="Buscar",
        query=True,
        type='search',
        content_type='movies'
    ))

    return itemlist


def search(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(HOST + '/?s=%s' % item.query, ).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<li class="col-md-12 itemlist"><div class="list-score">([^<]+)</div><div class="col-xs-2">' \
             '<div class="row"> <a href="([^"]+)" title="([^"]+)"> <img src="([^"]+)" title="[^"]+" alt="[^"]+" />.*?' \
             '<p class="main-info-list">.*?(\d+)</p><p class="text-list">(.*?)</p></div></li>'

    for rat, url, title, poster, year, plot in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            title=title,
            url=url,
            poster=poster,
            year=year,
            plot=plot,
            type='movie',
            content_type='servers',
            action='findvideos'
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data, '<a href="([^"]+)" ><i class="glyphicon glyphicon-chevron-right" '
                                                    'aria-hidden="true"></i></a>')
    if next_url:
        itemlist.append(item.clone(url=next_url, type='next'))

    return itemlist


def years(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(
        data,
        '<div class="menu-generos-container"><ul id="menu-generos" class="menu">(.*?)<div class="visible-desktop">'
    )

    patron = '<li id="[^"]+" class="menu-item menu-item-type-taxonomy menu-item-object-year_relase menu-item-[^"]+">' \
             '<a href="([^"]+)">(\d{4})</a></li>'

    for url, year in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            action='contents',
            label=year,
            url=url,
            content_type='movies',
            year=year
        ))

    return itemlist


def generos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(
        data,
        '<div class="menu-generos-container"><ul id="menu-generos" class="menu">(.*?)<div class="visible-desktop">'
    )

    patron = '<li id="[^"]+" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-[^"]+">' \
             '<a href="([^"]+)">([^<]+)</a></li>'

    for url, genre in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            action='contents',
            label=genre,
            url=url,
            content_type='movies'
        ))

    return itemlist


def newest(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url or HOST).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="col-mt-5 postsh"><div class="poster-media-card"> <a href="([^"]+)" title="[^"]+">' \
             '<div class="poster"><div class="title"> <span class="under-title">(.*?)(?:\(([\d]{4})\))?</span></div> ' \
             '<span class="rating"> <i class="glyphicon glyphicon-star"></i><span class="rating-number">[^<]+</span> ' \
             '</span><div class="poster-image-container"> <img width="300" height="428" src="([^"]+)" title="[^"]+" ' \
             'alt="[^"]+" /></div></div> </a></div></div'

    for url, title, year, poster in scrapertools.find_multiple_matches(data, patron):
        new_item = item.clone(
            title=title.split('(')[0],
            url=url,
            poster=poster,
            year=year,
            type='movie',
            content_type='servers',
            action='findvideos'
        )

        itemlist.append(new_item)

    # Paginador
    next_url = scrapertools.find_single_match(data,
                                              '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right" '
                                              'aria-hidden="true"></i></a>')
    if next_url:
        itemlist.append(item.clone(url=next_url, type='next'))

    return itemlist


def contents(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="col-mt-5 postsh"><div class="poster-media-card"> <a href="([^"]+)" title="[^"]+">' \
             '<div class="poster"><div class="title"> <span class="under-title">(.*?)(?:\(([\d]{4})\))?</span></div> ' \
             '<span class="rating"> <i class="glyphicon glyphicon-star"></i><span class="rating-number">[^<]+</span> ' \
             '</span><div class="poster-image-container"> <img width="300" height="428" src="([^"]+)" title="[^"]+" ' \
             'alt="[^"]+" /></div></div> </a></div></div'

    for url, title, year, poster in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            title=title,
            url=url,
            poster=poster,
            year=year or item.year,
            type='movie',
            content_type='servers',
            action='findvideos'
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data, '<a href="([^"]+)"\s?><i class="glyphicon glyphicon-chevron-right" '
                                                    'aria-hidden="true"></i></a>')
    if next_url:
        itemlist.append(item.clone(url=next_url, type='next'))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = 'href="#embed(\d*)" data-src="([^"]+)" class="([^"]+)"'
    for num, url, lang in scrapertools.find_multiple_matches(data, patron):
        qlt = scrapertools.find_single_match(
            data,
            '<div class="tab-pane reproductor repron[^"]+" id="embed%s"><div class="calishow">([^<]+)</div>' % num
        )

        try:
            b_64 = urllib.unquote_plus(scrapertools.find_single_match(url, 'redirect/\?id=([^&]+)'))
            b_64 = b_64 + '=' * (4 - len(b_64) % 4)
            url = base64.b64decode(b_64)
        except Exception:
            url = httptools.downloadpage(url.replace('/?', '?'), headers={'Referer': item.url},
                                         follow_redirects=False).headers['location']
        new_item = item.clone(
            url=url,
            type='server',
            lang=LNG.get(lang),
            quality=QLT.get(qlt),
            action='play',
            headers={'Referer': HOST} if 'streamango' in url or 'openload' in url else None
        )

        if not item.lang or new_item.lang in item.lang:
            itemlist.append(new_item)

    return servertools.get_servers_itemlist(itemlist)

