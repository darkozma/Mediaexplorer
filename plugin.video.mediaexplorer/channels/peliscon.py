# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'http://peliscon.com'

LNG = Languages({
    Languages.sub_es: ['sub', 'subtitulado'],
    Languages.en: ['en'],
    Languages.es: ['es', 'español'],
    Languages.la: ['lat', 'latino']
})
QLT = Qualities({
    Qualities.rip: ['rip'],
    Qualities.scr: ['screener'],
    Qualities.hd_full: ['1080p'],
    Qualities.hd: ['720p'],
})


def mainlist(item):
    logger.trace()
    itemlist = list()

    new_item = item.clone(
        type='label',
        label="Películas",
        category='movie',
        thumb='thumb/movie.png',
        icon='icon/movie.png',
        poster='poster/movie.png'
    )
    itemlist.append(new_item)
    itemlist.extend(menupeliculas(new_item))

    new_item = item.clone(
        type='label',
        label="Series",
        category='tvshow',
        thumb='thumb/tvshow.png',
        icon='icon/tvshow.png',
        poster='poster/tvshow.png',
    )
    itemlist.append(new_item)
    itemlist.extend(menuseries(new_item))

    return itemlist


def menupeliculas(item):
    logger.trace()
    itemlist = list()

    url = HOST + '/peliculas/'

    itemlist.append(item.clone(
        action="contents",
        label="Novedades",
        url=url,
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="search",
        label="Buscar",
        query=True,
        url=url,
        type='search',
        group=True,
        content_type='movies'
    ))

    return itemlist


def menuseries(item):
    logger.trace()
    itemlist = list()

    url = HOST + '/series/'

    itemlist.append(item.clone(
        action="contents",
        label="Series actualizadas",
        url=url,
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="newest_episodes",
        label="Nuevos episodios",
        url=HOST + "/episodios/",
        type="item",
        group=True,
        content_type='episodes'
    ))

    itemlist.append(item.clone(
        action="search",
        label="Buscar",
        query=True,
        url=url,
        type='search',
        group=True,
        content_type='tvshows'
    ))

    return itemlist


def contents(item):
    logger.trace()
    itemlist = list()

    if item.category == 'movie':
        patron = '(?s)<header class="archive_post"(.*?)<div class="sidebar scrolling">'
    else:
        patron = '(?s)<div id="archive-content"(.*?)<div class="sidebar scrolling">'

    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, patron)

    patron = '(?s)<article id="[^>]+>'
    patron += '<div class="poster"><img src="([^"]+).*?<a href="([^"]+).*?'
    patron += '<div class="animation-1 dtinfo"><div class="title">(.*?)<span>(\d{4})</span>'

    for poster, url, class_title, year in scrapertools.find_multiple_matches(data, patron):
        title = scrapertools.find_single_match(class_title, '>([^<]+)</')

        new_item = item.clone(
            label=title,
            title=title,
            url=url,
            poster=poster,
            type=item.category,
            year=year)

        if item.category == 'movie':
            flags = set(scrapertools.find_multiple_matches(class_title, 'themes/dooplay/assets/img/flags/([^.]+)'))
            if not flags:
                flags = {'unk'}

            new_item.lang = [LNG.get(l) for l in list(flags)]
            new_item.content_type = 'servers'
            new_item.action = 'findvideos'
        else:
            new_item.tvshowtitle = title
            new_item.content_type = 'seasons'
            new_item.action = 'seasons'

        itemlist.append(new_item)

    # Paginador
    next_url = scrapertools.find_single_match(data, '(?s)<a href="([^"]+)"><span class="icon-chevron-right">')
    if next_url:
        itemlist.append(item.clone(
            action=item.action,
            url=next_url,
            type='next'
        ))

    return itemlist


def seasons(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '<div class="se-q">[^>]+>(\d+)</span><span class="title">([^<]+)'

    for num_season, title in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            season=int(num_season),
            title=title.strip(),
            action="episodes",
            type='season',
            content_type='episodes'))

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '(?s)<div class="se-q">[^>]+>\s*%s\s*</span>(.*?)</ul></div></div>' % item.season
    data = scrapertools.find_single_match(data, patron)

    patron = '(?s)<img src="([^"]+)"></a></div><div class="numerando">([^<]+).*?<a href="([^"]+)">([^<]+)'

    for thumb, episode, url, title in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(episode.replace('-', 'x').replace(' ', ''))

        itemlist.append(item.clone(
            title=title,
            url=url,
            thumb=thumb.replace('/w150/', '/original/'),
            action="findvideos",
            episode=num_episode,
            season=num_season,
            type='episode',
            content_type='servers'
        ))

    return itemlist


def newest_episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '(?s)<article class="item se episodes" id="[^"]+"><div class="poster"><img src="([^"]+).*?'
    patron += '<a href="([^"]+)"><span class="b">([^<]+).*?'
    patron += '<span class="c">([^<]+).*?<div class="data">(.*?)</article>'

    for thumb, url, episode, tvshowtitle, flags in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(episode)

        flags = list(set(scrapertools.find_multiple_matches(flags, 'themes/dooplay/assets/img/flags/([^.]+)')))
        if not flags:
            flags = []

        itemlist.append(item.clone(
            tvshowtitle=tvshowtitle,
            label=tvshowtitle,
            url=url,
            thumb=thumb,
            lang=[LNG.get(l) for l in flags],
            action="findvideos",
            episode=num_episode,
            season=num_season,
            type='episode',
            content_type='servers'
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data, '(?s)<a href="([^"]+)"><span class="icon-chevron-right">')
    if next_url:
        itemlist.append(item.clone(
            action=item.action,
            url=next_url,
            type='next'
        ))

    return itemlist


def search(item):
    logger.trace()

    itemlist = list()
    item.url += '?s=%s' % item.query.replace(" ", "+")

    data = httptools.downloadpage(item.url).data
    patron = '(?s)<div class="result-item"><article>.*?<img src="([^"]+).*?'
    patron += '<a href="([^"]+)">([^<]+).*?'
    patron += '<span class="year">(\d{4})</span>(.*?)</div>'

    for poster, url, title, year, flags in scrapertools.find_multiple_matches(data, patron):
        new_item = item.clone(
            label=title,
            title=title,
            url=url,
            poster=poster.replace('/w90/', '/original/'),
            type=item.category,
            year=year)

        if flags:
            # movie
            flags = list(set(scrapertools.find_multiple_matches(flags, 'themes/dooplay/assets/img/flags/([^.]+)')))
            if not flags:
                flags = []

        if item.category == 'movie':
            new_item.lang = [LNG.get(l) for l in flags]
            new_item.content_type = 'servers'
            new_item.action = 'findvideos'

        else:
            # TVShow
            new_item.tvshowtitle = title
            new_item.content_type = 'seasons'
            new_item.action = 'seasons'

        itemlist.append(new_item)

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    # Opciones en el reproductor
    patron = '(?s)<div id="([^"]+)" class="play-box-iframe fixidtab"><iframe class="metaframe rptss" src="([^"]+)'
    opciones_reproductor = dict()
    for option, url in scrapertools.find_multiple_matches(data, patron):
        opciones_reproductor[option] = url

    patron = '(?s)<a class="options" href="#([^"]+)">.*?/img/flags/([^.]+).png">'
    for option, lang in scrapertools.find_multiple_matches(data, patron):
        if option in opciones_reproductor:
            itemlist.append(item.clone(
                url=opciones_reproductor.get(option),
                action='play',
                type='server',
                lang=LNG.get(lang),
                quality=Qualities.unk,
                stream=True
            ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    # Enlaces
    patron = '(?s)<td><img src="https://s2.googleusercontent.com/s2/favicons\?domain=([^.]+).*?'
    patron += '<a href="([^"]+)"[^>]+>([^<]+)</a></td><td>([^<]+)</td><td>([^<]+)'

    enlaces = []
    for server, url, type, quality, lang in scrapertools.find_multiple_matches(data, patron):
        quality = quality.lower()
        if 'screener' in quality:
            quality = 'screener'
        elif 'rip' in quality:
            quality = 'rip'

        enlaces.append(item.clone(
            url=url,
            action='play',
            type='server',
            lang=LNG.get(lang.lower()),
            quality=QLT.get(quality),
            server=server,
            stream=False if 'Descarga' in type else True
        ))

    itemlist.extend(servertools.get_servers_from_id(enlaces))

    return itemlist


def play(item):
    logger.trace()

    if item.url.startswith(HOST):
        data = httptools.downloadpage(item.url).data
        item.url = scrapertools.find_single_match(data, '<div class="boton reloading"><a href="([^"]+)"')
        servertools.normalize_url(item)
    return item
