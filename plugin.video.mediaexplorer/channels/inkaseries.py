# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'https://www.inkaseries.net'

LNG = Languages({
    Languages.es: ['castellano'],
    Languages.la: ['latino'],
    Languages.vos: ['subtitulado'],
})

QLT = Qualities({
    Qualities.hd: ['HD Real 720'],
    Qualities.rip: ['Dvd Rip'],

    Qualities.sd: ['dvdfull'],
    Qualities.hd_full: ['hdfull', 'hd1080'],
    Qualities.scr: ['screener']
})

def mainlist(item):
    logger.trace()
    itemlist = list()

    """"new_item = item.clone(
        type='label',
        label="Series",
        category='tvshow',
        icon='icon/tvshow.png',
        poster='poster/tvshow.png',
    )"""

    itemlist.append(item.clone(
        action="tvshows",
        label="Nuevas series",
        url=HOST + "/ultimas-series-agregadas/",
        type="item",
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="newest_episodes",
        label="Episodios de estreno",
        url=HOST + '/ultimos-capitulos-agregados/',
        type="item",
        content_type='episodes'
    ))

    itemlist.append(item.clone(
        action="tvshows",
        label="Series más vistas",
        url=HOST + "/categoria/series-mas-vistas/",
        type="item",
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="tvshows",
        label="Temporadas actualizadas",
        url=HOST + '/ultimas-temporadas-agregadas/',
        type="item",
        content_type='seasons'
    ))

    # "Series por género"
    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST,
        type="item"
    ))

    # "Buscar"
    itemlist.append(item.clone(
        action="search",
        label="Buscar",
        query=True,
        type='search',
        category='tvshow',
        content_type='tvshows'
    ))

    return itemlist


def generos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '<li><a href="([^"]+)"><span class="glyphicon glyphicon-expand" aria-hidden="true">' \
             '<\/span> <i>([^<]+)<\/i> <b>(\d+)'

    for url, label, num in scrapertools.find_multiple_matches(data, patron):
        if label in ['Destacadas', 'Recomendadas', 'Series más vistas', 'Soap', 'Uncategorized']:
            continue

        itemlist.append(item.clone(
            action="tvshows",
            label="%s (%s)" %(label, num),
            type="item",
            content_type='tvshows',
            url=url
        ))

    return itemlist


def search(item):
    logger.trace()
    item.url = "%s/?s=%s" %(HOST, item.query.replace(" ", "+"))

    return tvshows(item)


def tvshows(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '<div class="col-md-80 lado2"><div class="list_f"><div class="tiulo-c">(.*?)</div><div class="clear">'

    data = scrapertools.find_single_match(data, patron)
    patron = '<a class="poster" href="([^"]+)" title="([^"]+)"> <img src="([^"]+).*?<span class="generos?">([^<]*)'

    for url, title, poster, extra in scrapertools.find_multiple_matches(data, patron):

        if '/ultimas-temporadas-agregadas/' in item.url:
            url, season = scrapertools.find_single_match(url, '(.*?)\/temporada-(\d+)')

            new_item = item.clone(
                action='episodes',
                label=extra,
                tvshowtitle=extra,
                title=extra,
                url=url,
                season=int(season),
                poster=poster,
                type='season',
                content_type='episodes')

        else:
            new_item = item.clone(
                action='seasons',
                label=title,
                tvshowtitle=title,
                title=title,
                url=url,
                poster=poster,
                type='tvshow',
                content_type='seasons')

        itemlist.append(new_item)

    # Si es necesario añadir paginacion
    next_page = scrapertools.find_single_match(data, '<div class="pagination ">.*?class="last".*?<a href="([^"]+)')
    if next_page:
        itemlist.append(item.clone(
            url=next_page,
            type='next'
        ))

    return itemlist


def seasons(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '<li class="larr fSeason season season-(.*?)<li class="episode episode-'

    for season in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            action="episodes",
            season=int(scrapertools.find_single_match(season, "Temporada (\d+)")),
            type='season',
            content_type='episodes'
        ))

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '<div class="episode-guide">(.*?)<div class="col-md-4 padl0">'

    data = scrapertools.find_single_match(data, patron)
    patron = '<tr><td> <a href="([^"]+)" title="([^"]+)".*?<td>(.*?)</td></tr>'

    for url, episode, langs in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(episode.replace(',',''))

        if num_season and num_season == item.season:
            itemlist.append(item.clone(
                title=item.tvshowtitle,
                url= url,
                action="findvideos",
                episode=num_episode,
                season=num_season,
                lang=[LNG.get(l.lower()) for l in scrapertools.find_multiple_matches(langs, 'title="([^"]+)"')],
                type='episode',
                content_type='servers'
            ))

    return itemlist


def newest_episodes(item):
    logger.trace()
    itemlist = list()
    logger.debug(item)

    data = httptools.downloadpage(item.url).data
    patron = '<div class="col-md-80 lado2"><div class="list_f"><div class="tiulo-c">(.*?)</div><div class="clear">'

    data = scrapertools.find_single_match(data, patron)
    patron = '<img src="([^"]*).*?<span class="genero">([^<]*)</span><h3 class="name"><a href="([^"]+)[^>]+>([^<]+)'

    for thumb, episode, url, title  in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(episode.replace('-', ''))

        new_item = item.clone(
            label=title,
            tvshowtitle=title,
            url= url,
            action="findvideos",
            episode=num_episode,
            season=num_season,
            type='episode',
            content_type='servers')

        if thumb:
            new_item.thumb = thumb.strip().replace("w185", "original")

        itemlist.append(new_item)

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    for tipo in ['online', 'descarga']:
        data = scrapertools.find_single_match(data, '<div id="%s".*?<tbody>(.*?)</tbody>' % tipo)
        patron = '<tr><td><a href="([^"]+).*?<td>.+?<td>([^<]+)</td><td>([^<]+)</td>'
        for url, lang, qlt in scrapertools.find_multiple_matches(data, patron):
            itemlist.append(item.clone(
                url=url,
                action='play',
                type='server',
                lang=LNG.get(lang.lower()),
                quality=QLT.get(qlt),
                stream=(tipo == 'online')
            ))

    return servertools.get_servers_itemlist(itemlist)

